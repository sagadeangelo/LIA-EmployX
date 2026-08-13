from __future__ import annotations

from pathlib import Path
from typing import Optional
import traceback
import uuid

from backend.modules.cv.services.extraction_service import (
    ExtractionService,
)
from backend.modules.cv.repositories.cv_repository import (
    CVRepository,
)
from backend.modules.cv.models.cv_document import (
    CVDocument,
)
from backend.modules.cv.mappers.professional_profile_mapper import (
    ProfessionalProfileMapper,
)

from backend.modules.profile.models.professional_profile import (
    ProfessionalProfile,
)
from backend.modules.profile.repositories.profile_repository import (
    ProfileRepository,
)

from backend.utils.logger import AppLogger

from backend.modules.mission.models import (
    Mission,
    MissionEventType,
)
from backend.runtime.mission_state import (
    MissionStage,
    MissionStatus,
)
from backend.modules.mission.repositories import (
    MissionRepository,
)
from backend.modules.mission.controller import (
    MissionController,
)


class CVService:
    """
    Coordina el procesamiento completo de un CV.

    Flujo:

        Upload
          ↓
        Mission
          ↓
        Archivo físico
          ↓
        ExtractionService
          ↓
        CVDocument
          ↓
        ProfessionalProfileMapper
          ↓
        ProfessionalProfile
          ↓
        ProfileRepository
          ↓
        Mission.profile_id
          ↓
        Runtime

    Cada CV procesado genera su propio ProfessionalProfile.

        CV #1 → Profile A
        CV #2 → Profile B
        CV #3 → Profile C

    Los perfiles anteriores no se sobrescriben.
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

        # Resultado temporal del procesamiento actual.
        self.last_document: CVDocument | None = None
        self.last_profile: ProfessionalProfile | None = None

    # ==================================================================
    # MAIN FLOW
    # ==================================================================

    def process_uploaded_cv(
        self,
        file_bytes: bytes,
        filename: str,
        mission_id: Optional[str] = None,
    ) -> Mission:
        """
        Procesa completamente un CV y crea/persiste su
        ProfessionalProfile asociado.

        Cada ejecución crea un perfil independiente.
        """

        start_time = AppLogger.get_time_ms()

        # Evitar contaminación entre ejecuciones.
        self.last_document = None
        self.last_profile = None

        # ==========================================================
        # 1. CREAR O RECUPERAR MISSION
        # ==========================================================

        if not mission_id:
            mission = Mission(
                title="Optimizar CV y Buscar Vacantes",
                career_goal=(
                    "Encontrar el trabajo ideal basado "
                    "en mi perfil actual"
                ),
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
                description=(
                    "Misión inicializada desde subida de CV."
                ),
                stage=MissionStage.RECEIVE_FILE,
                duration=int(
                    AppLogger.get_time_ms()
                    - start_time
                ),
            )

        else:
            mission = self.mission_repo.get_by_id(
                mission_id
            )

            if mission is None:
                raise ValueError(
                    f"Mission {mission_id} no encontrada."
                )

            mission.status = MissionStatus.UPLOADING
            self.mission_repo.save(mission)

        # ==========================================================
        # 2. GUARDAR ARCHIVO
        # ==========================================================

        current_stage = MissionStage.STORE_FILE

        AppLogger.info(
            "Storage",
            f"Guardando archivo temporal: {filename}",
            mission_id=mission_id,
        )

        try:
            mission.current_step = current_stage
            self.mission_repo.save(mission)

            temp_dir = Path("data/uploads")
            temp_dir.mkdir(
                parents=True,
                exist_ok=True,
            )

            safe_filename = Path(filename).name

            file_path = (
                temp_dir
                / f"{uuid.uuid4().hex}_{safe_filename}"
            )

            with file_path.open("wb") as file:
                file.write(file_bytes)

            storage_duration = (
                AppLogger.get_time_ms()
                - start_time
            )

            AppLogger.info(
                "Storage",
                "Archivo guardado exitosamente",
                mission_id=mission_id,
                duration_ms=storage_duration,
            )

            mission.state.file_path = str(file_path)
            mission.status = MissionStatus.STORED

            self.mission_repo.save(mission)

            self.mission_controller.log_event(
                mission_id=mission_id,
                source="CVService",
                event_type=MissionEventType.CV_UPLOADED,
                title="CV Subido y Guardado",
                description=(
                    f"Se ha recibido y guardado "
                    f"el archivo: {filename}"
                ),
                metadata={
                    "filename": filename,
                    "stored_path": str(file_path),
                },
                stage=current_stage,
                duration=int(storage_duration),
            )

            # ======================================================
            # 3. EXTRAER CVDocument
            # ======================================================

            current_stage = MissionStage.BUILD_PROFILE

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

            parse_duration = (
                AppLogger.get_time_ms()
                - parse_start
            )

            self.last_document = document

            AppLogger.info(
                "Parser",
                "CVDocument generado correctamente",
                mission_id=mission_id,
                duration_ms=parse_duration,
            )

            # ======================================================
            # 4. CVDocument → ProfessionalProfile
            # ======================================================

            AppLogger.info(
                "Profile",
                "Convirtiendo CVDocument a ProfessionalProfile...",
                mission_id=mission_id,
            )

            profile_start = AppLogger.get_time_ms()

            professional_profile = (
                ProfessionalProfileMapper.from_cv_document(
                    document
                )
            )

            profile_duration = (
                AppLogger.get_time_ms()
                - profile_start
            )

            self.last_profile = professional_profile

            AppLogger.info(
                "Profile",
                (
                    "ProfessionalProfile generado correctamente "
                    f"[profile_id={professional_profile.id}]"
                ),
                mission_id=mission_id,
                duration_ms=profile_duration,
            )

            # ======================================================
            # 5. PERSISTIR PROFESSIONAL PROFILE
            # ======================================================

            current_stage = MissionStage.SAVE_PROFILE

            AppLogger.info(
                "Profile",
                (
                    "Persistiendo ProfessionalProfile "
                    f"[profile_id={professional_profile.id}]"
                ),
                mission_id=mission_id,
            )

            profile_repository = ProfileRepository()

            saved_profile = profile_repository.save(
                professional_profile
            )

            self.last_profile = saved_profile

            AppLogger.info(
                "Profile",
                (
                    "ProfessionalProfile persistido correctamente "
                    f"[profile_id={saved_profile.id}]"
                ),
                mission_id=mission_id,
            )

            # ======================================================
            # 6. ASOCIAR PROFILE_ID A LA MISSION
            # ======================================================

            current_stage = MissionStage.UPDATE_RUNTIME

            profile_id = saved_profile.id

            mission.profile_id = profile_id

            if hasattr(
                mission.state,
                "profile_id",
            ):
                mission.state.profile_id = profile_id

            self.mission_repo.save(mission)

            AppLogger.info(
                "Mission",
                (
                    "ProfessionalProfile asociado a la Mission "
                    f"[profile_id={profile_id}]"
                ),
                mission_id=mission_id,
            )

            # ======================================================
            # 7. EVENTO PROFILE_CREATED
            # ======================================================

            self.mission_controller.log_event(
                mission_id=mission_id,
                source="CVService",
                event_type=MissionEventType.PROFILE_CREATED,
                title="Perfil Profesional Generado",
                description=(
                    "El CV fue convertido y persistido "
                    "como ProfessionalProfile."
                ),
                metadata={
                    "profile_id": profile_id,
                    "filename": filename,
                },
                stage=current_stage,
                duration=int(
                    AppLogger.get_time_ms()
                    - start_time
                ),
            )

            # ======================================================
            # 8. FINALIZAR MISSION
            # ======================================================

            mission.status = MissionStatus.COMPLETED
            mission.current_step = MissionStage.COMPLETE

            self.mission_repo.save(mission)

            AppLogger.info(
                "CVService",
                (
                    "CV procesado completamente: "
                    "CVDocument → ProfessionalProfile → Mission "
                    f"[profile_id={profile_id}]"
                ),
                mission_id=mission_id,
                duration_ms=int(
                    AppLogger.get_time_ms()
                    - start_time
                ),
            )

            return mission

        except Exception as error:
            # ======================================================
            # ERROR
            # ======================================================

            AppLogger.error(
                "CVService",
                (
                    f"Fallo procesando CV en "
                    f"{current_stage.value}: {error}"
                ),
                mission_id=mission_id,
                duration_ms=int(
                    AppLogger.get_time_ms()
                    - start_time
                ),
            )

            mission.status = MissionStatus.FAILED
            mission.failureReason = type(error).__name__

            self.mission_repo.save(mission)

            self.mission_controller.log_event(
                mission_id=mission_id,
                source="CVService",
                event_type=MissionEventType.MISSION_FAILED,
                title=(
                    f"Fallo en etapa "
                    f"{current_stage.value}"
                ),
                description=(
                    f"Error al procesar archivo: "
                    f"{str(error)}"
                ),
                severity="error",
                stage=current_stage,
                developerMessage=str(error),
                logs=traceback.format_exc(),
                duration=int(
                    AppLogger.get_time_ms()
                    - start_time
                ),
            )

            raise