from __future__ import annotations

from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)

from backend.modules.cv.services.cv_service import CVService
from backend.modules.cv.services.extraction_service import (
    ExtractionService,
)
from backend.modules.cv.repositories.cv_repository import (
    CVRepository,
)

from backend.modules.mission.controller import MissionController
from backend.modules.mission.repositories import (
    MissionRepository,
    MissionEventRepository,
)

from backend.runtime.runtime_registry import (
    get_runtime_registry,
)

from backend.utils.logger import AppLogger
from backend.storage.json_provider import JsonStorageProvider

from backend.modules.cv.models.upload_response import (
    UploadMissionResponse,
)

from backend.modules.mission.models import (
    MissionSnapshot,
    RuntimeStatus,
    SystemHealth,
)


router = APIRouter(
    prefix="/api/v1/cv",
    tags=["CV"],
)


# ======================================================================
# DEPENDENCY INJECTION
# ======================================================================

def get_cv_service() -> CVService:
    """
    Construye el CVService utilizando las dependencias reales
    del RuntimeRegistry.
    """

    storage = JsonStorageProvider()

    mission_repo = MissionRepository(
        storage,
    )

    event_repo = MissionEventRepository(
        storage,
    )

    # --------------------------------------------------------------
    # Runtime / Agent Registry
    # --------------------------------------------------------------

    runtime_registry = get_runtime_registry()

    agent_registry = (
        runtime_registry._agent_registry
    )

    mission_controller = MissionController(
        mission_repo,
        event_repo,
        agent_registry,
    )

    return CVService(
        extraction_service=ExtractionService(),
        cv_repo=CVRepository(),
        mission_controller=mission_controller,
        mission_repo=mission_repo,
    )


# ======================================================================
# UPLOAD CV
# ======================================================================

@router.post(
    "/upload",
    response_model=UploadMissionResponse,
)
async def upload_cv(
    file: UploadFile = File(...),
    mission_id: Optional[str] = Form(None),
    cv_service: CVService = Depends(
        get_cv_service,
    ),
) -> UploadMissionResponse:
    """
    Endpoint principal para procesar un CV.

    Flujo:

        archivo
            ↓
        CVService
            ↓
        CVDocument
            ↓
        ProfessionalProfile
            ↓
        persistencia
            ↓
        Mission.profile_id
            ↓
        UploadMissionResponse

    La respuesta mantiene separados:

        cv
            → CVDocument

        profile
            → ProfessionalProfile

    Esto es importante porque el modelo CVDocument actual
    NO contiene un campo id ni professional_profile_id.
    """

    start_time = AppLogger.get_time_ms()

    AppLogger.info(
        "Backend",
        "Petición POST /api/v1/cv/upload recibida",
        mission_id=mission_id,
    )

    # ==================================================================
    # 1. VALIDAR ARCHIVO
    # ==================================================================

    if file is None:
        AppLogger.error(
            "Backend",
            "No se recibió ningún UploadFile",
            mission_id=mission_id,
        )

        raise HTTPException(
            status_code=400,
            detail="No se recibió ningún archivo.",
        )

    # ==================================================================
    # 2. LEER ARCHIVO
    # ==================================================================

    file_bytes = await file.read()

    if not file_bytes:
        AppLogger.error(
            "Backend",
            "El archivo recibido está vacío.",
            mission_id=mission_id,
        )

        raise HTTPException(
            status_code=400,
            detail="El archivo está vacío.",
        )

    filename = file.filename or "cv"

    AppLogger.info(
        "Backend",
        (
            f"Archivo recibido en FastAPI: "
            f"nombre: {filename}, "
            f"tamaño: {len(file_bytes)} bytes, "
            f"Content-Type: {file.content_type}"
        ),
        mission_id=mission_id,
    )

    # ==================================================================
    # 3. PROCESAR CV
    # ==================================================================

    AppLogger.info(
        "Backend",
        "Delegando a CVService.process_uploaded_cv...",
        mission_id=mission_id,
    )

    mission = cv_service.process_uploaded_cv(
        file_bytes=file_bytes,
        filename=filename,
        mission_id=mission_id,
    )

    duration = (
        AppLogger.get_time_ms()
        - start_time
    )

    AppLogger.info(
        "Backend",
        "CV procesado. Preparando respuesta...",
        mission_id=mission.id,
        duration_ms=duration,
    )

    # ==================================================================
    # 4. OBTENER RESULTADOS DEL CVSERVICE
    # ==================================================================

    cv_document = cv_service.last_document

    professional_profile = (
        cv_service.last_profile
    )

    # ------------------------------------------------------------------
    # CVDocument
    # ------------------------------------------------------------------

    if cv_document is None:
        AppLogger.error(
            "Backend",
            (
                "El CV fue procesado pero "
                "CVService.last_document es None."
            ),
            mission_id=mission.id,
        )

        raise RuntimeError(
            "CVDocument no fue generado por CVService."
        )

    # ------------------------------------------------------------------
    # ProfessionalProfile
    # ------------------------------------------------------------------

    if professional_profile is None:
        AppLogger.error(
            "Backend",
            (
                "El CV fue procesado pero "
                "CVService.last_profile es None."
            ),
            mission_id=mission.id,
        )

        raise RuntimeError(
            "ProfessionalProfile no fue generado "
            "por CVService."
        )

    # ==================================================================
    # 5. VALIDAR PROFILE ID
    # ==================================================================

    profile_id = str(
        professional_profile.id
    ).strip()

    if not profile_id:
        AppLogger.error(
            "Backend",
            (
                "ProfessionalProfile generado "
                "sin un ID válido."
            ),
            mission_id=mission.id,
        )

        raise RuntimeError(
            "ProfessionalProfile no tiene un ID válido."
        )

    AppLogger.info(
        "Profile",
        (
            "ProfessionalProfile listo para enviar "
            f"[profile_id={profile_id}]"
        ),
        mission_id=mission.id,
    )

    # ==================================================================
    # 6. INICIAR RUNTIME
    # ==================================================================

    cv_service.mission_controller.trigger_engine(
        mission.id,
    )

    # ==================================================================
    # 7. OBTENER EVENTOS
    # ==================================================================

    mission_events = (
        cv_service
        .mission_controller
        .event_repo
        .get_by_mission(
            mission.id,
        )
    )

    # ==================================================================
    # 8. CONSTRUIR SNAPSHOT
    # ==================================================================

    snapshot = MissionSnapshot(
        mission=mission,
        runtime=RuntimeStatus(
            online=True,
            active_agents=mission.active_agents,
            current_agent=mission.current_agent,
        ),
        timeline=mission_events,
        progress=mission.progress,
        current_step=mission.current_step.value,
        results=mission.outputs,
        health=SystemHealth(
            status="ok",
            database=True,
            storage=True,
            version="1.0.0",
        ),
        warnings=mission.warnings,
        errors=mission.errors,
        availableActions=(
            cv_service
            .mission_controller
            .get_available_actions(
                mission,
            )
        ),
        retryMode=(
            cv_service
            .mission_controller
            .get_retry_mode(
                mission,
            )
        ),
    )

    # ==================================================================
    # 9. CONSTRUIR RESPUESTA
    # ==================================================================
    #
    # IMPORTANTE:
    #
    # cv
    #   = CVDocument
    #
    # profile
    #   = ProfessionalProfile
    #
    # No intentamos meter profile_id dentro de CVDocument porque
    # el modelo actual no posee ese campo.
    # ==================================================================

    response = UploadMissionResponse(
        snapshot=snapshot,
        cv=cv_document,
        profile=professional_profile,
    )

    # ==================================================================
    # 10. LOG FINAL
    # ==================================================================

    AppLogger.info(
        "Backend",
        (
            "UploadMissionResponse construido correctamente "
            f"[mission_id={mission.id}] "
            f"[profile_id={profile_id}]"
        ),
        mission_id=mission.id,
        duration_ms=(
            AppLogger.get_time_ms()
            - start_time
        ),
    )

    return response