from __future__ import annotations

import os
from pathlib import Path

from backend.agents.base.base_agent import BaseAgent, AgentMetadata
from backend.agents.base.agent_context import AgentContext
from backend.agents.base.agent_result import AgentResult
from backend.modules.cv.services.extraction_service import ExtractionService
from backend.modules.mission.models import MissionEvent, MissionEventType
from backend.runtime.mission_state import MissionStage
from backend.modules.profile.repositories.profile_repository import ProfileRepository
from backend.modules.cv.mappers.professional_profile_mapper import ProfessionalProfileMapper


class CVParserAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.extraction_service = ExtractionService()

    @property
    def metadata(self) -> AgentMetadata:
        return AgentMetadata(
            id="cv_parser",
            name="CV Parser",
            version="2.0.0",
            author="LIA Team",
            description="Lee el archivo del CV, extrae su texto y detecta secciones clave.",
            capabilities=["document_parsing", "text_extraction", "section_detection"],
            dependencies=[],
            priority=10,
            enabled=True,
        )

    def can_execute(self, context: AgentContext) -> bool:
        has_file = bool(
            context.mission.state.file_path
            and os.path.exists(context.mission.state.file_path)
        )
        return has_file and context.mission.state.metadata is None

    async def execute(self, context: AgentContext) -> AgentResult:
        file_path = context.mission.state.file_path
        if not file_path or not os.path.exists(file_path):
            return AgentResult.failure("El archivo no existe o la ruta es inválida.")

        self._set_status("running")
        self.log(f"Iniciando extracción de texto para: {file_path}")

        try:
            cv_document = self.extraction_service.process(
                Path(file_path),
                mission_id=context.mission.id,
            )
            cv_doc_dict = cv_document.model_dump(mode="json")

            events = [
                MissionEvent(
                    mission_id=context.mission.id,
                    type=MissionEventType.TEXT_EXTRACTED,
                    source="CVParser",
                    title="Extracción Completada",
                    description="El texto del documento fue extraído y estructurado.",
                    stage=MissionStage.EXTRACT_TEXT,
                    metadata={
                        "language": (
                            cv_document.detected_language.language
                            if cv_document.detected_language
                            else "unknown"
                        ),
                        "sections": len(cv_document.sections),
                    },
                )
            ]

            self._set_progress(100)
            self._set_status("completed")
            self.log("Parseo de documento completado exitosamente.")

            repo = ProfileRepository()
            profile_id = context.mission.state.profile_id
            profile = repo.get_by_id(profile_id) if profile_id else None

            if profile is None:
                profile = ProfessionalProfileMapper.from_cv_document(cv_document)
                profile.user_id = context.mission.user_id
                repo.save(profile)

            return AgentResult.ok(
                progress=100,
                recommendations=["Texto extraído. Listo para análisis profundo."],
                events=events,
                memory_updates={
                    "metadata": cv_document.metadata,
                    "raw_text": cv_doc_dict.get("raw_text"),
                    "sections": cv_doc_dict.get("sections"),
                    "profile_id": profile.id,
                },
            )

        except Exception as exc:
            self.log(f"Error parseando documento: {exc}")
            return AgentResult.failure(f"Error extrayendo texto: {exc}")
