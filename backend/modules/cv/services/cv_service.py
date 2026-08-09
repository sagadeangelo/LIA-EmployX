from typing import Optional
from pathlib import Path
import traceback
import uuid

from backend.modules.cv.services.extraction_service import ExtractionService
from backend.modules.cv.repositories.cv_repository import CVRepository
from backend.modules.cv.models.cv_document import CVDocument
from backend.utils.logger import AppLogger

from backend.modules.mission.models import Mission, MissionEventType
from backend.runtime.mission_state import MissionStage, MissionStatus
from backend.modules.mission.repositories import MissionRepository
from backend.modules.mission.controller import MissionController


class CVService:
    """
    Coordina la lógica del negocio de CVs.

    Responsabilidades:

    - Crear o recuperar la Mission.
    - Guardar físicamente el CV.
    - Ejecutar el pipeline estructurado de extracción.
    - Mantener disponible el CVDocument resultante.
    - Notificar al MissionController.

    El procesamiento estructurado continúa delegándose
    completamente a ExtractionService.
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

        # Último documento estructurado procesado por este servicio.
        self.last_document: CVDocument | None = None

    def process_uploaded_cv(
        self,
        file_bytes: bytes,
        filename: str,
        mission_id: Optional[str] = None,
    ) -> Mission:
        """
        Guarda y procesa un CV subido.

        El resultado estructurado queda disponible en:

            self.last_document

        mientras la Mission continúa siendo el objeto de
        coordinación del Runtime.
        """

        start_time = AppLogger.get_time_ms()

        # =====================================================
        # 1. CREAR O RECUPERAR MISSION
        # =====================================================

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
                    AppLogger.get_time_ms() - start_time
                ),
            )

        else:
            mission = self.mission_repo.get_by_id(mission_id)

            if not mission:
                raise ValueError(
                    f"Mission {mission_id} no encontrada."
                )

            mission.status = MissionStatus.UPLOADING
            self.mission_repo.save(mission)

        # =====================================================
        # 2. GUARDAR ARCHIVO
        # =====================================================

        AppLogger.info(
            "Storage",
            f"Guardando archivo temporal: {filename}",
            mission_id=mission_id,
        )

        current_stage = MissionStage.STORE_FILE

        try:
            mission.current_step = current_stage
            self.mission_repo.save(mission)

            temp_dir = Path("data/uploads")
            temp_dir.mkdir(
                parents=True,
                exist_ok=True,
            )

            file_path = (
                temp_dir
                / f"{uuid.uuid4().hex}_{filename}"
            )

            with open(file_path, "wb") as file:
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

            # Asignar archivo a la Mission.
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
                },
                stage=current_stage,
                duration=int(storage_duration),
            )

            # =================================================
            # 3. PROCESAMIENTO ESTRUCTURADO
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

            # =================================================
            # 4. PERSISTENCIA DEL CV
            # =================================================

            # Si CVRepository ya dispone de un método de
            # persistencia compatible, se podrá conectar aquí.
            #
            # Por ahora NO inventamos una llamada al repository.
            # El CVDocument permanece disponible mediante
            # self.last_document y el flujo existente de Mission
            # continúa sin romperse.

            return mission

        except Exception as error:
            AppLogger.error(
                "CVService",
                (
                    f"Fallo procesando CV en "
                    f"{current_stage.value}: {error}"
                ),
                mission_id=mission_id,
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