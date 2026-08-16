"""
LIA EmployX — MissionController (Refactorizado - Fase 3)

Orquestador del Agent Collaboration Engine.

Principios:
  - Obtiene agentes del AgentRegistry. Nunca los instancia directamente.
  - Construye AgentContext inmutable antes de cada ciclo.
  - Propaga AgentResult entre agentes actualizando SharedMemory via merge().
  - Es el UNICO que aplica cambios de estado al contexto y a la mision.
  - Ningún agente conoce a otro ni llama a repositorios.
"""

from __future__ import annotations

import logging
from typing import List, Optional

from backend.agents.base.agent_context import AgentContext, MissionHistory
from backend.agents.base.shared_memory import SharedMemoryKey
from backend.agents.base.agent_registry import AgentRegistry
from backend.agents.base.agent_result import AgentResult
from backend.agents.base.shared_memory import SharedMemory
from backend.modules.mission.models import (
    Mission,
    MissionEvent,
    MissionEventType,
    AgentStatusInfo,
)
from backend.runtime.mission_state import MissionStage, MissionStatus, ACTIVE_STATUSES
from backend.modules.mission.repositories import (
    MissionRepository,
    MissionEventRepository,
)
from backend.modules.mission.task_executor import TaskExecutor
from backend.modules.profile.repositories.profile_repository import ProfileRepository

logger = logging.getLogger(__name__)


class MissionController:
    """
    Orquestador del pipeline de agentes.

    Flujo por ciclo:
        trigger_engine()
            └── TaskExecutor.execute(_run_mission_cycle)
                    ├── _build_context(mission)       → AgentContext
                    ├── registry.get_all_agents()     → List[BaseAgent] (ordenados por prioridad)
                    └── for each agent:
                            ├── agent.can_execute(context)?
                            ├── result = await agent.execute(context)
                            ├── context = _apply_result(context, result)   ← solo MC aplica cambios
                            ├── _persist_events(result.events)
                            └── _update_mission_progress(mission, agents)
    """

    def __init__(
        self,
        mission_repo: MissionRepository,
        event_repo: MissionEventRepository,
        registry: AgentRegistry,
    ):
        if not isinstance(registry, AgentRegistry):
            raise TypeError(
                f"MissionController esperaba AgentRegistry y recibió {type(registry).__name__}. "
                "Revisa la inyección de dependencias en cv_controller.py y missions.py."
            )
        self.mission_repo = mission_repo
        self.event_repo = event_repo
        self.registry: AgentRegistry = registry

    # ------------------------------------------------------------------
    # API Pública
    # ------------------------------------------------------------------

    def load_mission(self, mission_id: str) -> Optional[Mission]:
        return self.mission_repo.get_by_id(mission_id)

    def log_event(
        self,
        mission_id: str,
        source: str,
        event_type: MissionEventType,
        title: str,
        description: str,
        severity: str = "info",
        metadata: dict = None,
        stage: MissionStage = MissionStage.RECEIVE_FILE,
        userMessage: Optional[str] = None,
        developerMessage: Optional[str] = None,
        logs: Optional[str] = None,
        duration: int = 0,
    ) -> None:
        event = MissionEvent(
            mission_id=mission_id,
            source=source,
            type=event_type,
            severity=severity,
            title=title,
            description=description,
            metadata=metadata or {},
            stage=stage,
            userMessage=userMessage,
            developerMessage=developerMessage,
            logs=logs,
            duration=duration,
        )
        self.event_repo.save(event)

        result_str = "FAILED" if severity == "error" else "SUCCESS"
        logger.info(
            f"[Mission: {mission_id}] Stage: {stage.value} Source: {source} Elapsed: {duration} ms Result: {result_str}"
        )

    def get_available_actions(self, mission: Mission) -> List[str]:
        if mission.status == MissionStatus.FAILED:
            if mission.current_step in [
                MissionStage.RECEIVE_FILE,
                MissionStage.STORE_FILE,
            ]:
                return ["RESTART", "CANCEL"]
            else:
                return ["RESUME", "RESTART", "CANCEL"]
        elif mission.status in [MissionStatus.CREATED, MissionStatus.PAUSED]:
            return ["RESUME", "CANCEL"]
        return []

    def get_retry_mode(self, mission: Mission) -> str:
        """Tells the client *how* to retry a failed mission.

        UPLOAD_REQUIRED  → File never persisted; must re-upload + create new mission.
        RESUME_ALLOWED   → Pipeline can resume from the failed step in-place.
        NONE             → Mission is not in a retryable state.
        """
        if mission.status != MissionStatus.FAILED:
            return "NONE"
        if mission.current_step in [MissionStage.RECEIVE_FILE, MissionStage.STORE_FILE]:
            return "UPLOAD_REQUIRED"
        return "RESUME_ALLOWED"

    def trigger_engine(self, mission_id: str) -> None:
        """Lanza el ciclo de agentes en segundo plano via TaskExecutor."""
        TaskExecutor.execute(self._run_mission_cycle, mission_id)

    def get_agent_status(self, mission_id: str) -> List[AgentStatusInfo]:
        """Devuelve el estado actual de todos los agentes registrados."""
        return [
            AgentStatusInfo(
                id=a.id,
                name=a.name,
                status=a.get_status(),
                progress=a.get_progress(),
                recommendations=a.get_recommendations(),
            )
            for a in self.registry.get_all_agents()
        ]

    # ------------------------------------------------------------------
    # Pipeline Interno
    # ------------------------------------------------------------------

    async def _run_mission_cycle(self, mission_id: str) -> None:
        mission = self.load_mission(mission_id)
        if not mission:
            logger.warning("Mission %s no encontrada.", mission_id)
            return

        # Cycle proceeds via State Machine
        if mission.status == MissionStatus.CREATED:
            mission.status = MissionStatus.UPLOADING
            self.mission_repo.save(mission)

        if mission.status in {MissionStatus.CREATED, MissionStatus.UPLOADING}:
            mission.status = MissionStatus.QUEUED
            self.mission_repo.save(mission)

        if mission.status not in ACTIVE_STATUSES:
            logger.warning(
                "Mission %s no está activa (status=%s) — ciclo omitido.",
                mission_id,
                mission.status.value,
            )
            return

        mission.status = MissionStatus.PROCESSING
        self.mission_repo.save(mission)

        logger.info("Iniciando ciclo de misión para: %s", mission_id)

        # 1. Construir el contexto inicial (inmutable desde la perspectiva de cada agente)
        context = self._build_context(mission)
        agents = self.registry.get_all_agents()

        if not agents:
            logger.warning("No hay agentes registrados en el AgentRegistry.")
            # Still mark as COMPLETED so Flutter stops polling
            mission.status = MissionStatus.COMPLETED
            mission.current_step = MissionStage.COMPLETE
            self.mission_repo.save(mission)
            return

        # 2. Pipeline secuencial: cada agente recibe el contexto actualizado del anterior
        for agent in agents:
            if not agent.metadata.enabled:
                continue

            if not agent.can_execute(context):
                logger.info("[%s] Precondiciones no cumplidas — omitido.", agent.name)
                self.log_event(
                    mission_id=mission_id,
                    source="MissionController",
                    event_type=MissionEventType.MISSION_PAUSED,
                    title=f"Agente Omitido: {agent.name}",
                    description=f"El agente no cumple precondiciones.",
                    severity="warning",
                    metadata={"agent_id": agent.id},
                )
                continue

            logger.info("[%s] Ejecutando...", agent.name)
            self.log_event(
                mission_id=mission_id,
                source="MissionController",
                event_type=MissionEventType.MISSION_STARTED,
                title=f"Ejecutando Agente: {agent.name}",
                description=f"El agente '{agent.name}' ha comenzado su ejecución.",
                metadata={"agent_id": agent.id},
            )

            try:
                result: AgentResult = await agent.execute(context)

                if result.success:
                    # 3. SOLO el MissionController aplica los cambios al contexto
                    context = self._apply_result(context, result, mission)
                    self._persist_events(result.events)
                    logger.info(
                        "[%s] Completado. Progress: %d%%", agent.name, result.progress
                    )
                    
                    # --- INICIO INSTRUMENTACIÓN TEMPORAL ---
                    print(f"\n=========================================")
                    print(f"Agent: {agent.name}")
                    print(f"memory_updates: {result.memory_updates}")
                    print(f"Context aplicado correctamente: TRUE")
                    print(f"Mission metadata: {context.mission.state.metadata is not None}")
                    print(f"profile_id: {context.mission.state.profile_id}")
                    print(f"cv_document (has_metadata): {context.mission.state.metadata is not None}")
                    skills = context.shared_memory.get(SharedMemoryKey.SKILLS, [])
                    skills_len = len(skills) if skills else 0
                    print(f"professional_profile (skills len): {skills_len}")
                    print(f"=========================================\n")
                    # --- FIN INSTRUMENTACIÓN TEMPORAL ---
                else:
                    logger.error("[%s] Falló: %s", agent.name, result.error)
                    self.log_event(
                        mission_id=mission_id,
                        source="MissionController",
                        event_type=MissionEventType.MISSION_FAILED,
                        title=f"Error en Agente: {agent.name}",
                        description=f"El agente falló con error: {result.error}",
                        severity="error",
                        metadata={"agent_id": agent.id, "error": result.error},
                    )

            except Exception as exc:
                logger.exception("[%s] Excepcion inesperada: %s", agent.name, str(exc))

        # 4. FINAL PROFILE TRACE — intentionally before COMPLETED.
        # This is diagnostic only: it does not mutate the profile or mission.
        self._trace_final_professional_profile(mission_id, mission, context)

        # 5. Mark mission COMPLETED and persist — this is what Flutter's poller waits for
        mission.status = MissionStatus.COMPLETED
        mission.current_step = MissionStage.COMPLETE
        self.mission_repo.save(mission)

        logger.info("Ciclo de misión completado. Progreso: %d%%", mission.progress)
        self.log_event(
            mission_id=mission_id,
            source="MissionController",
            event_type=MissionEventType.MISSION_COMPLETED,
            title="Ciclo de Misión Completado",
            description=f"El motor de agentes terminó. Progreso actual: {mission.progress}%.",
            metadata={"progress": mission.progress},
        )

    def _trace_final_professional_profile(
        self,
        mission_id: str,
        mission: Mission,
        context: AgentContext,
    ) -> None:
        """
        Diagnóstico quirúrgico de la persistencia del ProfessionalProfile.

        Se ejecuta inmediatamente antes de marcar la misión como COMPLETED.
        Lee el perfil DOS veces:
          1. desde el contexto de la misión;
          2. desde ProfileRepository, que vuelve a leer profiles.json.

        Así podemos distinguir entre:
          - el pipeline no produjo scores;
          - los scores existen pero no se persistieron;
          - los scores sí quedaron persistidos y Flutter recibe otra cosa.
        """
        profile_id = mission.state.profile_id or context.mission.state.profile_id

        if not profile_id:
            logger.error(
                "[PROFILE_TRACE][%s] SIN profile_id antes de COMPLETED. "
                "No se puede verificar la persistencia del ProfessionalProfile.",
                mission_id,
            )
            return

        try:
            repository = ProfileRepository()
            profile = repository.get_by_id(profile_id)

            if profile is None:
                logger.error(
                    "[PROFILE_TRACE][%s] profile_id=%s NO EXISTE en ProfileRepository "
                    "inmediatamente antes de COMPLETED.",
                    mission_id,
                    profile_id,
                )
                return

            logger.info(
                "[PROFILE_TRACE][%s] IN-MEMORY/REPOSITORY profile_id=%s "
                "ats=%s linkedin=%s cv=%s skills=%s employability=%s",
                mission_id,
                profile.id,
                profile.ats_metrics.ats_score,
                profile.linkedin_metrics.score,
                profile.cv_score,
                len(profile.skills.technical_skills),
                profile.career_metrics.employability_level,
            )

            logger.info(
                "[PROFILE_TRACE][%s] METRICS_DETAILS profile_id=%s "
                "ats_keywords=%s ats_missing=%s linkedin_recommendations=%s "
                "career_strengths=%s career_weaknesses=%s",
                mission_id,
                profile.id,
                len(profile.ats_metrics.detected_keywords),
                len(profile.ats_metrics.missing_keywords),
                len(profile.linkedin_metrics.recommendations),
                len(profile.career_metrics.strengths),
                len(profile.career_metrics.weaknesses),
            )

            if (
                profile.ats_metrics.ats_score == 0
                and profile.linkedin_metrics.score == 0
                and profile.cv_score == 0
            ):
                logger.error(
                    "[PROFILE_TRACE][%s] ALERTA: los tres scores principales siguen en 0 "
                    "justo antes de COMPLETED. El problema está antes de Flutter.",
                    mission_id,
                )
            else:
                logger.info(
                    "[PROFILE_TRACE][%s] OK: al menos un score fue persistido antes de COMPLETED.",
                    mission_id,
                )

        except Exception:
            logger.exception(
                "[PROFILE_TRACE][%s] Error leyendo/verificando ProfessionalProfile antes de COMPLETED.",
                mission_id,
            )

    def _build_context(self, mission: Mission) -> AgentContext:
        """Construye el AgentContext inicial para un ciclo de misión."""
        events = self.event_repo.get_by_mission(mission.id)
        completed = [
            e.type.value for e in events
        ]  # MissionEvent uses .type, not .event_type

        return AgentContext(
            mission=mission,
            history=MissionHistory(
                completed_stages=completed,
                current_stage="starting",
                total_events=len(events),
            ),
            current_step=mission.current_step.value,
            shared_memory=SharedMemory(mission.metadata.get("shared_memory", {})),
            recommendations=mission.metadata.get("recommendations", []),
            events=[],
        )

    def _apply_result(
        self,
        context: AgentContext,
        result: AgentResult,
        mission: Mission,
    ) -> AgentContext:
        """
        UNICO lugar donde se aplican los cambios al contexto.
        Crea un NUEVO contexto con el State actualizado (inmutabilidad).
        Fusiona recomendaciones del agente con las acumuladas.
        """
        # Propaga MissionState
        updated_context = context.with_memory_updates(result.memory_updates)

        # Fusiona recomendaciones (acumulativo, no sobrescribe)
        updated_context.recommendations = (
            context.recommendations + result.recommendations
        )

        # Actualiza misión si el agente la modificó
        if result.updated_mission:
            mission.progress = result.updated_mission.progress
            mission.status = result.updated_mission.status

        # Persist memory and recommendations back to mission
        mission.state = updated_context.mission.state
        mission.metadata["shared_memory"] = updated_context.shared_memory.snapshot()
        mission.metadata["recommendations"] = updated_context.recommendations

        return updated_context

    def _persist_events(self, events: List[MissionEvent]) -> None:
        for event in events:
            self.event_repo.save(event)
