from fastapi import APIRouter, UploadFile, File, Form, Depends
from typing import Optional

from backend.modules.cv.services.cv_service import CVService
from backend.modules.cv.services.extraction_service import ExtractionService
from backend.modules.cv.repositories.cv_repository import CVRepository
from backend.modules.mission.controller import MissionController
from backend.modules.mission.repositories import MissionRepository, MissionEventRepository
from backend.runtime.runtime_registry import get_runtime_registry

router = APIRouter(prefix="/api/v1/cv", tags=["CV"])

from backend.utils.logger import AppLogger
from backend.storage.json_provider import JsonStorageProvider
from backend.modules.cv.models.upload_response import UploadMissionResponse
from backend.modules.mission.models import MissionSnapshot, RuntimeStatus, SystemHealth


# Dependency Injection â€” wired to the global RuntimeRegistry initialized at lifespan
def get_cv_service() -> CVService:
    storage = JsonStorageProvider()
    mission_repo = MissionRepository(storage)
    event_repo = MissionEventRepository(storage)

    # Pull the real AgentRegistry from the global RuntimeRegistry singleton.
    # build_registry() already ran at app startup (runtime_registry.py:47).
    # Passing the list is the bug; we pass the registry object itself.
    runtime_registry = get_runtime_registry()
    agent_registry = runtime_registry._agent_registry   # AgentRegistry instance

    mission_controller = MissionController(mission_repo, event_repo, agent_registry)

    return CVService(
        extraction_service=ExtractionService(),
        cv_repo=CVRepository(),
        mission_controller=mission_controller,
        mission_repo=mission_repo
    )

@router.post("/upload")
async def upload_cv(
    file: UploadFile = File(...),
    mission_id: Optional[str] = Form(None),
    cv_service: CVService = Depends(get_cv_service)
):
    """
    Endpoint que coordina la carga de un CV, lo procesa mediante el CVService y notifica a la MisiÃ³n.
    """
    start_time = AppLogger.get_time_ms()
    AppLogger.info("Backend", "PeticiÃ³n POST /api/v1/cv/upload recibida", mission_id=mission_id)
    
    if not file:
        AppLogger.error("Backend", "Error: No se recibiÃ³ ningÃºn UploadFile", mission_id=mission_id)
        return {"status": "error", "message": "No file"}

    file_bytes = await file.read()
    
    AppLogger.info("Backend", f"Archivo recibido en FastAPI: nombre: {file.filename}, tamaÃ±o: {len(file_bytes)} bytes, Content-Type: {file.content_type}", mission_id=mission_id)
    
    # Delegar lÃ³gica al CVService (Solo guarda y encola)
    AppLogger.info("Backend", "Delegando a CVService.process_uploaded_cv...", mission_id=mission_id)
    
    mission = cv_service.process_uploaded_cv(
        file_bytes=file_bytes, 
        filename=file.filename, 
        mission_id=mission_id
    )
    
    duration = AppLogger.get_time_ms() - start_time
    AppLogger.info("Backend", "CV Procesado. Iniciando Runtime...", mission_id=mission.id, duration_ms=duration)
    
    # 5. El controlador orquesta el inicio del Runtime
    cv_service.mission_controller.trigger_engine(mission.id)
    
    # 6. Construir el Snapshot y devolver UploadMissionResponse
    mission_events = cv_service.mission_controller.event_repo.get_by_mission(mission.id)
    
    snapshot = MissionSnapshot(
        mission=mission,
        runtime=RuntimeStatus(online=True, active_agents=mission.active_agents, current_agent=mission.current_agent),
        timeline=mission_events,
        progress=mission.progress,
        current_step=mission.current_step.value,
        results=mission.outputs,
        health=SystemHealth(status="ok", database=True, storage=True, version="1.0.0"),
        warnings=mission.warnings,
        errors=mission.errors,
        availableActions=cv_service.mission_controller.get_available_actions(mission),
        retryMode=cv_service.mission_controller.get_retry_mode(mission),
    )
    
    response = UploadMissionResponse(
    snapshot=snapshot,
    cv=cv_service.last_document,
)
    
    return response

