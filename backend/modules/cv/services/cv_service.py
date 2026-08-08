from typing import Optional
from pathlib import Path
import uuid
import shutil

from backend.modules.cv.services.extraction_service import ExtractionService
from backend.modules.cv.repositories.cv_repository import CVRepository
from backend.modules.cv.models.cv_document import CVDocument
from backend.utils.logger import AppLogger

from backend.modules.mission.models import Mission, MissionEventType
from backend.runtime.mission_state import MissionStage, MissionStatus
from backend.modules.mission.repositories import MissionRepository
from backend.modules.mission.controller import MissionController
import traceback

class CVService:
    """
    Coordina la lógica del negocio de CVs.
    Usa el ExtractionService para procesar y CVRepository para persistir.
    Notifica al MissionController sobre nuevos CVs.
    """
    
    def __init__(
        self, 
        extraction_service: ExtractionService, 
        cv_repo: CVRepository,
        mission_controller: MissionController,
        mission_repo: MissionRepository
    ):
        self.extraction_service = extraction_service
        self.cv_repo = cv_repo
        self.mission_controller = mission_controller
        self.mission_repo = mission_repo

    def process_uploaded_cv(self, file_bytes: bytes, filename: str, mission_id: Optional[str] = None) -> Mission:
        start_time = AppLogger.get_time_ms()
        
        # 1. Crear o recuperar la Mission
        if not mission_id:
            mission = Mission(
                title="Optimizar CV y Buscar Vacantes", 
                career_goal="Encontrar el trabajo ideal basado en mi perfil actual",
                status=MissionStatus.UPLOADING,
                current_step=MissionStage.RECEIVE_FILE
            )
            self.mission_repo.save(mission)
            mission_id = mission.id
            self.mission_controller.log_event(
                mission_id=mission_id,
                source="CVService",
                event_type=MissionEventType.MISSION_CREATED,
                title="Misión Creada",
                description="Misión inicializada desde subida de CV.",
                stage=MissionStage.RECEIVE_FILE,
                duration=int(AppLogger.get_time_ms() - start_time)
            )
        else:
            mission = self.mission_repo.get_by_id(mission_id)
            if not mission:
                raise ValueError(f"Mission {mission_id} no encontrada.")
            mission.status = MissionStatus.UPLOADING
            self.mission_repo.save(mission)

        AppLogger.info("Storage", f"Guardando archivo temporal: {filename}", mission_id=mission_id)
        
        current_stage = MissionStage.STORE_FILE
        try:
            mission.current_step = current_stage
            self.mission_repo.save(mission)

            temp_dir = Path("data/uploads")
            temp_dir.mkdir(parents=True, exist_ok=True)
            file_path = temp_dir / f"{uuid.uuid4().hex}_{filename}"
            
            with open(file_path, "wb") as f:
                f.write(file_bytes)

            storage_duration = AppLogger.get_time_ms() - start_time
            AppLogger.info("Storage", "Archivo guardado exitosamente", mission_id=mission_id, duration_ms=storage_duration)
            
            # Asignar archivo a la misión
            mission.state.file_path = str(file_path)
            mission.status = MissionStatus.STORED
            self.mission_repo.save(mission)

            self.mission_controller.log_event(
                mission_id=mission_id,
                source="CVService",
                event_type=MissionEventType.CV_UPLOADED,
                title="CV Subido y Guardado",
                description=f"Se ha recibido y guardado el archivo: {filename}",
                metadata={"filename": filename},
                stage=current_stage,
                duration=int(storage_duration)
            )
            
            return mission

        except Exception as e:
            AppLogger.error("CVService", f"Fallo procesando CV en {current_stage.value}: {e}", mission_id=mission_id)
            mission.status = MissionStatus.FAILED
            mission.failureReason = type(e).__name__
            self.mission_repo.save(mission)

            self.mission_controller.log_event(
                mission_id=mission_id,
                source="CVService",
                event_type=MissionEventType.MISSION_FAILED,
                title=f"Fallo en etapa {current_stage.value}",
                description=f"Error al guardar archivo: {str(e)}",
                severity="error",
                stage=current_stage,
                developerMessage=str(e),
                logs=traceback.format_exc(),
                duration=int(AppLogger.get_time_ms() - start_time)
            )
            raise e
