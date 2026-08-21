"""
jobs_proxy.py

Proxy hacia la API de FreeHire (https://freehire.me).

Flutter Web no puede llamar directamente a FreeHire porque el servidor
externo no devuelve el header Access-Control-Allow-Origin en sus
respuestas CORS.

Este módulo expone los endpoints de empleos de LIA y reenvía las
peticiones hacia FreeHire a través del backend.

IMPORTANTE
----------
FreeHire aplica correctamente los filtros de búsqueda mediante:

    GET /api/v1/jobs/search

Por ello, el endpoint local:

    GET /api/v1/jobs

también utiliza internamente /jobs/search.

Esto permite que parámetros como:

    countries=mx
    q=software
    limit=20
    offset=0

sean respetados de forma consistente.

Endpoints expuestos:

    GET /api/v1/jobs
        → https://freehire.me/api/v1/jobs/search

    GET /api/v1/jobs/search
        → https://freehire.me/api/v1/jobs/search
"""

from __future__ import annotations

import logging
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/jobs",
    tags=["jobs-proxy"],
)

_FREEHIRE_SEARCH_URL = "https://freehire.me/api/v1/jobs/search"
_TIMEOUT = 25.0


# ============================================================================
# Helpers
# ============================================================================


def _build_search_params(
    *,
    q: str,
    countries: str,
    limit: int,
    offset: int,
) -> dict[str, Any]:
    """
    Construye los parámetros que serán enviados a FreeHire.

    Los parámetros vacíos no se envían para evitar alterar el
    comportamiento del endpoint remoto.
    """

    params: dict[str, Any] = {
        "limit": limit,
        "offset": offset,
    }

    normalized_q = q.strip()
    normalized_countries = countries.strip()

    if normalized_q:
        params["q"] = normalized_q

    if normalized_countries:
        params["countries"] = normalized_countries

    return params


async def fetch_freehire_payload(params: dict[str, Any]) -> dict[str, Any]:
    """
    Realiza la petición HTTP cruda a FreeHire y devuelve el payload JSON.
    No captura excepciones de httpx.
    """
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        response = await client.get(
            _FREEHIRE_SEARCH_URL,
            params=params,
            headers={
                "Accept": "application/json",
            },
        )
    response.raise_for_status()
    return response.json()


async def _request_freehire(
    *,
    params: dict[str, Any],
) -> JSONResponse:
    """
    Ejecuta la petición contra FreeHire y normaliza los errores
    para el backend de LIA.
    """

    logger.info(
        "[JobsProxy] GET FreeHire /jobs/search params=%s",
        params,
    )

    try:
        payload = await fetch_freehire_payload(params)

        data_count = len(payload.get("data", [])) if isinstance(payload, dict) else 0

        logger.info(
            "[JobsProxy] FreeHire /jobs/search → 200 (%d jobs)",
            data_count,
        )

        return JSONResponse(
            content=payload,
            status_code=200,
        )

    except httpx.TimeoutException as exc:
        logger.error(
            "[JobsProxy] Timeout al conectar con FreeHire: %s",
            exc,
        )

        raise HTTPException(
            status_code=504,
            detail="FreeHire no respondió a tiempo.",
        ) from exc

    except httpx.HTTPStatusError as exc:
        status_code = exc.response.status_code

        logger.error(
            "[JobsProxy] FreeHire respondió con HTTP %s",
            status_code,
        )

        raise HTTPException(
            status_code=status_code,
            detail=f"FreeHire devolvió {status_code}.",
        ) from exc

    except ValueError as exc:
        logger.error(
            "[JobsProxy] FreeHire devolvió una respuesta JSON inválida: %s",
            exc,
        )

        raise HTTPException(
            status_code=502,
            detail="FreeHire devolvió una respuesta inválida.",
        ) from exc

    except httpx.RequestError as exc:
        logger.error(
            "[JobsProxy] Error de conexión con FreeHire: %s",
            exc,
        )

        raise HTTPException(
            status_code=502,
            detail="No se pudo conectar con FreeHire.",
        ) from exc

    except Exception as exc:
        logger.exception(
            "[JobsProxy] Error inesperado comunicando con FreeHire: %s",
            exc,
        )

        raise HTTPException(
            status_code=502,
            detail="Error inesperado al consultar FreeHire.",
        ) from exc


# ============================================================================
# GET /api/v1/jobs
# ============================================================================


@router.get("")
async def get_jobs(
    q: str = Query(
        default="",
        description="Término de búsqueda profesional.",
    ),
    countries: str = Query(
        default="",
        description="Código o códigos de país aceptados por FreeHire. Ejemplo: mx.",
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Número máximo de vacantes.",
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Desplazamiento para paginación.",
    ),
) -> JSONResponse:
    """
    Obtiene vacantes desde FreeHire.

    Aunque el endpoint local se mantiene como:

        GET /api/v1/jobs

    internamente utiliza:

        GET https://freehire.me/api/v1/jobs/search

    Esto es necesario porque FreeHire aplica correctamente filtros
    como `countries` mediante el endpoint /search.
    """

    params = _build_search_params(
        q=q,
        countries=countries,
        limit=limit,
        offset=offset,
    )

    logger.info(
        "[JobsProxy] GET /api/v1/jobs → FreeHire /jobs/search params=%s",
        params,
    )

    return await _request_freehire(params=params)


# ============================================================================
# GET /api/v1/jobs/search
# ============================================================================


@router.get("/search")
async def search_jobs(
    q: str = Query(
        default="",
        description="Término de búsqueda profesional.",
    ),
    countries: str = Query(
        default="",
        description="Código o códigos de país aceptados por FreeHire. Ejemplo: mx.",
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Número máximo de vacantes.",
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Desplazamiento para paginación.",
    ),
) -> JSONResponse:
    """
    Busca vacantes en FreeHire.

    Proxy directo hacia:

        https://freehire.me/api/v1/jobs/search
    """

    params = _build_search_params(
        q=q,
        countries=countries,
        limit=limit,
        offset=offset,
    )

    logger.info(
        "[JobsProxy] GET /api/v1/jobs/search → "
        "FreeHire /jobs/search params=%s",
        params,
    )

    return await _request_freehire(params=params)