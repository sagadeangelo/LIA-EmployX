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


async def _request_freehire_tiered(
    *,
    q: str,
    countries: str,
    city: str,
    region: str,
    limit: int,
    offset: int,
) -> JSONResponse:
    """
    Ejecuta una búsqueda jerárquica: Ciudad -> Región/Estado -> Nacional.

    Si no se especifica ciudad ni región, ejecuta la búsqueda estándar directa.
    Si se especifica ciudad/región, recopila primero las vacantes hiperlocales
    y complementa con las regionales y nacionales sin duplicar registros.
    """
    base_q = q.strip()
    norm_countries = countries.strip()
    norm_city = city.strip()
    norm_region = region.strip()

    if not norm_city and not norm_region:
        params = _build_search_params(
            q=base_q,
            countries=norm_countries,
            limit=limit,
            offset=offset,
        )
        return await _request_freehire(params=params)

    logger.info(
        "[JobsProxy] Tiered search q='%s', countries='%s', city='%s', region='%s', limit=%d",
        base_q,
        norm_countries,
        norm_city,
        norm_region,
        limit,
    )

    queries_to_try: list[tuple[str, str]] = []
    if norm_city:
        queries_to_try.append(("city", f"{base_q} {norm_city}".strip()))

    if norm_region and norm_region.lower() != norm_city.lower():
        queries_to_try.append(("region", f"{base_q} {norm_region}".strip()))

    queries_to_try.append(("country", base_q))

    collected_jobs: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    total_found = 0

    try:
        for tier_name, query_str in queries_to_try:
            if len(collected_jobs) >= limit:
                break

            needed = limit - len(collected_jobs)
            fetch_limit = min(max(needed, 20), 100)
            params: dict[str, Any] = {
                "limit": fetch_limit,
                "offset": 0,
            }
            if query_str:
                params["q"] = query_str
            if norm_countries:
                params["countries"] = norm_countries

            payload = await fetch_freehire_payload(params)
            jobs = payload.get("data", []) if isinstance(payload, dict) else []
            meta = payload.get("meta", {}) if isinstance(payload, dict) else {}
            total_found = max(total_found, meta.get("total", 0))

            for job in jobs:
                if not isinstance(job, dict):
                    continue
                job_id = str(job.get("id") or job.get("public_slug") or job.get("external_id") or job.get("url") or "")
                if not job_id:
                    job_id = f"{job.get('title')}_{job.get('company')}_{job.get('location')}"

                if job_id not in seen_ids:
                    seen_ids.add(job_id)
                    collected_jobs.append(job)
                    if len(collected_jobs) >= limit:
                        break

        logger.info(
            "[JobsProxy] Tiered search completed → 200 (%d jobs)",
            len(collected_jobs),
        )

        return JSONResponse(
            content={
                "data": collected_jobs,
                "meta": {
                    "limit": limit,
                    "offset": offset,
                    "total": total_found or len(collected_jobs),
                },
            },
            status_code=200,
        )

    except httpx.TimeoutException as exc:
        logger.error("[JobsProxy] Timeout al conectar con FreeHire: %s", exc)
        raise HTTPException(status_code=504, detail="FreeHire no respondió a tiempo.") from exc
    except httpx.HTTPStatusError as exc:
        status_code = exc.response.status_code
        logger.error("[JobsProxy] FreeHire respondió con HTTP %s", status_code)
        raise HTTPException(status_code=status_code, detail=f"FreeHire devolvió {status_code}.") from exc
    except ValueError as exc:
        logger.error("[JobsProxy] FreeHire devolvió una respuesta JSON inválida: %s", exc)
        raise HTTPException(status_code=502, detail="FreeHire devolvió una respuesta inválida.") from exc
    except httpx.RequestError as exc:
        logger.error("[JobsProxy] Error de conexión con FreeHire: %s", exc)
        raise HTTPException(status_code=502, detail="No se pudo conectar con FreeHire.") from exc
    except Exception as exc:
        logger.exception("[JobsProxy] Error inesperado comunicando con FreeHire: %s", exc)
        raise HTTPException(status_code=502, detail="Error inesperado al consultar FreeHire.") from exc


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
    city: str = Query(
        default="",
        description="Ciudad detectada para búsqueda hiperlocal.",
    ),
    region: str = Query(
        default="",
        description="Región o estado detectado para búsqueda regional.",
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
    Obtiene vacantes desde FreeHire con soporte para búsqueda jerárquica
    geográfica (ciudad -> región -> país).
    """

    return await _request_freehire_tiered(
        q=q,
        countries=countries,
        city=city,
        region=region,
        limit=limit,
        offset=offset,
    )


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
    city: str = Query(
        default="",
        description="Ciudad detectada para búsqueda hiperlocal.",
    ),
    region: str = Query(
        default="",
        description="Región o estado detectado para búsqueda regional.",
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
    Busca vacantes en FreeHire con soporte para búsqueda jerárquica
    geográfica (ciudad -> región -> país).
    """

    return await _request_freehire_tiered(
        q=q,
        countries=countries,
        city=city,
        region=region,
        limit=limit,
        offset=offset,
    )