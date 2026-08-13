from typing import Optional
from pathlib import Path
import hashlib
import traceback
import uuid

from backend.modules.cv.services.extraction_service import ExtractionService
from backend.modules.cv.repositories.cv_repository import CVRepository
from backend.modules.cv.models.cv_document import CVDocument
from backend.modules.cv.mappers.professional_profile_mapper import ProfessionalProfileMapper
from backend.modules.profile.models.professional_profile import ProfessionalProfile
from backend.modules.profile.repositories.profile_repository import ProfileRepository
from backend.utils.logger import AppLogger

from backend.modules.mission.models import Mission, MissionEventType
from backend.runtime.mission_state import MissionStage, MissionStatus
from backend.modules.mission.repositories import MissionRepository
from backend.modules.mission.controller import MissionController


class CVService:
    """
    Coordinates the upload boundary and canonical CV persistence.

    The upload path performs extraction once, maps the canonical
    CVDocument into the ProfessionalProfile consumed by the UI/agents,
    and persists both before the asynchronous Mission runtime starts.
    """

    def __init__(
        self,
        extraction_service: ExtractionService,
        cv_repo: CVRepository,
        mission_controller: MissionController,
        mission_repo: MissionRepository,
    ) -> None:
        self.extraction_service = extraction_service
        self.cv_repo = cv_repo
        self.mission_controller = mission_controller
        self.mission_repo = mission_repo
        self.profile_repo = ProfileRepository()

        self.last_document: CVDocument | None = None
        self.last_profile: ProfessionalProfile | None = None

    def process_uploaded_cv(
        self,
        file_bytes: bytes,
        filename: str,
        mission_id: Optional[str] = None,
    ) -> Mission:
        start_time = AppLogger.get_time_ms()

        # =====================================================
        # 1. CREATE OR RECOVER MISSION
        # =====================================================
        if not mission_id:
            mission = Mission(
                title="Optimizar CV y Buscar Vacantes",
                career_goal="Encontrar el trabajo ideal basado en mi perfil actual",
                status=MissionStatus.UPLOADING,
                current_step=MissionStage.RECEIVE_FILE,
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
                duration=int(AppLogger.get_time_ms() - start_time),
            )
        else:
            mission = self.mission_repo.get_by_id(mission_id)
            if not mission:
                raise ValueError(f"Mission {mission_id} no encontrada.")
            mission.status = MissionStatus.UPLOADING
            self.mission_repo.save(mission)

        # =====================================================
        # 2. SAVE FILE
        # =====================================================
        current_stage = MissionStage.STORE_FILE

        try:
            mission.current_step = current_stage
            self.mission_repo.save(mission)

            temp_dir = Path("data/uploads")
            temp_dir.mkdir(parents=True, exist_ok=True)

            safe_name = Path(filename).name
            file_path = temp_dir / f"{uuid.uuid4().hex}_{safe_name}"

            with open(file_path, "wb") as file:
                file.write(file_bytes)

            storage_duration = AppLogger.get_time_ms() - start_time
            mission.state.file_path = str(file_path)
            mission.status = MissionStatus.STORED
            self.mission_repo.save(mission)

            self.mission_controller.log_event(
                mission_id=mission_id,
                source="CVService",
                event_type=MissionEventType.CV_UPLOADED,
                title="CV Subido y Guardado",
                description=f"Se ha recibido y guardado el archivo: {safe_name}",
                metadata={"filename": safe_name, "bytes": len(file_bytes)},
                stage=current_stage,
                duration=int(storage_duration),
            )

            if not file_bytes:
                raise ValueError("El archivo recibido está vacío (0 bytes).")

            # =================================================
            # 3. STRUCTURED EXTRACTION — exactly once here
            # =================================================
            AppLogger.info(
                "Parser",
                "Iniciando ExtractionService.process...",
                mission_id=mission_id,
            )
            parse_start = AppLogger.get_time_ms()

            document = self.extraction_service.process(
                file_path=file_path,
                mission_id=mission_id,
            )

            parse_duration = AppLogger.get_time_ms() - parse_start
            document.metadata.sha256 = hashlib.sha256(file_bytes).hexdigest()
            document.user_id = mission.user_id

            self.last_document = document

            # =================================================
            # 4. CREATE / PERSIST PROFESSIONAL PROFILE
            # =================================================
            profile = ProfessionalProfileMapper.from_cv_document(document)
            profile.user_id = mission.user_id
            self.profile_repo.save(profile)

            document.profile_id = profile.id
            self.cv_repo.save(document)

            mission.profile_id = profile.id
            mission.state.profile_id = profile.id
            mission.current_step = MissionStage.SAVE_PROFILE
            self.mission_repo.save(mission)

            self.last_profile = profile

            AppLogger.info(
                "Parser",
                "CVDocument y ProfessionalProfile persistidos correctamente.",
                mission_id=mission_id,
                duration_ms=parse_duration,
            )

            self.mission_controller.log_event(
                mission_id=mission_id,
                source="CVService",
                event_type=MissionEventType.PROFILE_CREATED,
                title="Perfil Profesional Creado",
                description="El CV fue convertido al perfil profesional persistente.",
                metadata={"profile_id": profile.id, "cv_id": document.id},
                stage=MissionStage.SAVE_PROFILE,
                duration=int(parse_duration),
            )

            return mission

        except Exception as error:
            AppLogger.error(
                "CVService",
                f"Fallo procesando CV en {current_stage.value}: {error}",
                mission_id=mission_id,
            )

            mission.status = MissionStatus.FAILED
            mission.failureReason = type(error).__name__
            self.mission_repo.save(mission)

            self.mission_controller.log_event(
                mission_id=mission_id,
                source="CVService",
                event_type=MissionEventType.MISSION_FAILED,
                title=f"Fallo en etapa {current_stage.value}",
                description=f"Error al procesar archivo: {str(error)}",
                severity="error",
                stage=current_stage,
                developerMessage=str(error),
                logs=traceback.format_exc(),
                duration=int(AppLogger.get_time_ms() - start_time),
            )

            raise
