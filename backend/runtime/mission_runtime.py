"""
LIA EmployX — Mission Runtime
Layer 4: MissionRuntime (Single Mission Execution Instance)

Una instancia de MissionRuntime gestiona el ciclo de vida completo de UNA misión:
  - Ejecutar el pipeline de agentes
  - Manejar transiciones de estado via la FSM
  - Heartbeat (para dashboards en tiempo real)
  - Cancellation Token (para detención limpia)
  - Emitir todos los eventos al RuntimeEventBus (NO al print())
  - Persistir el estado después de cada cambio

No conoce Flutter. No conoce SSE. Solo ejecuta, persiste y emite eventos.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Optional

from backend.agents.base.agent_context import AgentContext, MissionHistory
from backend.agents.base.agent_registry import AgentRegistry
from backend.agents.base.shared_memory import SharedMemory
from backend.modules.mission.models import Mission, MissionEvent, MissionEventType
from backend.modules.mission.repositories import (
    MissionRepository,
    MissionEventRepository,
)
from backend.runtime.event_bus import RuntimeEventBus
from backend.runtime.mission_state import (
    MissionStatus,
    VALID_STATUS_TRANSITIONS,
    TERMINAL_STATUSES,
    can_transition_status,
)
from backend.runtime.runtime_events import (
    MissionStarted,
    MissionCompleted,
    MissionFailed,
    MissionPaused,
    MissionCancelled,
    MissionResumed,
    MissionRecovered,
    AgentStarted,
    AgentCompleted,
    AgentSkipped,
    AgentFailed,
    RuntimeHeartbeat,
)

logger = logging.getLogger(__name__)


class CancellationToken:
    """Token para solicitar cancelación limpia de una misión en ejecución."""

    def __init__(self) -> None:
        self._cancelled = False

    def cancel(self) -> None:
        self._cancelled = True

    @property
    def is_cancelled(self) -> bool:
        return self._cancelled


class MissionRuntime:
    """
    Ejecutor y gestor de estado de una única misión.

    Responsabilidades:
      1. Mantener el estado de la misión (FSM formal)
      2. Ejecutar el pipeline de agentes secuencialmente
      3. Persistir estado tras cada cambio
      4. Emitir eventos tipados al EventBus
      5. Soportar pausa, cancelación y recovery
      6. Publicar heartbeats para dashboards
    """

    def __init__(
        self,
        mission: Mission,
        mission_repo: MissionRepository,
        event_repo: MissionEventRepository,
        registry: AgentRegistry,
        bus: RuntimeEventBus,
    ) -> None:
        self.mission = mission
        self._repo = mission_repo
        self._event_repo = event_repo
        self._registry = registry
        self._bus = bus
        self._cancellation = CancellationToken()
        self._started_at: Optional[datetime] = None

    # ─────────────────────────────────────────────
    # Propiedades de inspección
    # ─────────────────────────────────────────────

    @property
    def mission_id(self) -> str:
        return self.mission.id

    @property
    def state(self) -> MissionStatus:
        return self.mission.status

    @property
    def current_agent(self) -> Optional[str]:
        return self.mission.current_agent

    @property
    def execution_seconds(self) -> float:
        if self._started_at is None:
            return 0.0
        return (datetime.utcnow() - self._started_at).total_seconds()

    # ─────────────────────────────────────────────
    # Control público
    # ─────────────────────────────────────────────

    async def run(self) -> None:
        """Inicia o reanuda la ejecución del pipeline de agentes."""
        if self._cancellation.is_cancelled:
            return
        await self._transition(self._resolve_runtime_start_state())
        await self._bus.publish(MissionStarted(mission_id=self.mission_id))
        self._started_at = datetime.utcnow()
        self.mission.execution_started_at = self._started_at
        await self._execute_pipeline()

    async def recover(self, previous_state: str) -> None:
        """Reanuda una misión interrumpida tras un reinicio del backend."""
        logger.info(
            "[Runtime:%s] Recovering from state=%s", self.mission_id, previous_state
        )
        await self._bus.publish(
            MissionRecovered(
                mission_id=self.mission_id,
                previous_state=previous_state,
            )
        )
        await self._transition(self._resolve_runtime_start_state())
        self._started_at = datetime.utcnow()
        self.mission.execution_started_at = self._started_at
        await self._execute_pipeline()

    async def pause(self, reason: str = "") -> None:
        """Pausa la misión. El agente actual puede terminar su ciclo actual."""
        await self._transition(MissionStatus.PAUSED)
        await self._bus.publish(
            MissionPaused(mission_id=self.mission_id, reason=reason)
        )
        self._persist()

    async def cancel(self, reason: str = "User requested") -> None:
        """Solicita cancelación limpia. El pipeline para en el próximo checkpoint."""
        self._cancellation.cancel()
        await self._transition(MissionStatus.CANCELLED)
        await self._bus.publish(
            MissionCancelled(mission_id=self.mission_id, reason=reason)
        )
        self._persist()

    # ─────────────────────────────────────────────
    # Pipeline interno
    # ─────────────────────────────────────────────

    async def _execute_pipeline(self) -> None:
        context = self._build_context()
        agents = self._registry.get_all_agents()

        if not agents:
            logger.warning(
                "[Runtime:%s] No hay agentes en el registry.", self.mission_id
            )
            await self._fail("No agents registered")
            return

        for agent in agents:
            # ── Checkpoint de cancelación ──
            if self._cancellation.is_cancelled:
                logger.info(
                    "[Runtime:%s] Cancelación solicitada — deteniendo.", self.mission_id
                )
                break

            if not agent.metadata.enabled:
                continue

            if not agent.can_execute(context):
                await self._bus.publish(
                    AgentSkipped(
                        mission_id=self.mission_id,
                        agent_id=agent.id,
                        agent_name=agent.name,
                        reason="Preconditions not met",
                    )
                )
                self._append_timeline(
                    f"[SKIP] {agent.name} — precondiciones no cumplidas"
                )
                continue

            # ── Iniciar agente ──
            self.mission.current_agent = agent.name
            await self._bus.publish(
                AgentStarted(
                    mission_id=self.mission_id,
                    agent_id=agent.id,
                    agent_name=agent.name,
                )
            )
            self._append_timeline(f"[START] {agent.name}")
            await self._heartbeat()

            try:
                result = await agent.execute(context)

                if result.success:
                    # Aplicar resultado al contexto (patrón inmutabilidad)
                    context = context.with_memory_updates(result.memory_updates)
                    context.recommendations = (
                        context.recommendations + result.recommendations
                    )

                    # Persistir SharedMemory en la Misión
                    self.mission.shared_memory = context.shared_memory.snapshot()
                    self.mission.metadata["recommendations"] = context.recommendations
                    self.mission.agents_executed.append(agent.name)

                    # Actualizar progreso si el agente lo reporta
                    if result.updated_mission:
                        self.mission.progress = result.updated_mission.progress

                    await self._bus.publish(
                        AgentCompleted(
                            mission_id=self.mission_id,
                            agent_id=agent.id,
                            agent_name=agent.name,
                            progress=result.progress,
                        )
                    )
                    self._append_timeline(f"[DONE] {agent.name} — {result.progress}%")

                    # Persistir eventos del agente
                    for event in result.events:
                        self._event_repo.save(event)

                else:
                    self.mission.errors.append(f"{agent.name}: {result.error}")
                    await self._bus.publish(
                        AgentFailed(
                            mission_id=self.mission_id,
                            agent_id=agent.id,
                            agent_name=agent.name,
                            error=result.error or "Unknown error",
                        )
                    )
                    self._append_timeline(f"[FAIL] {agent.name} — {result.error}")

            except Exception as exc:
                error_msg = f"{agent.name}: {exc}"
                self.mission.errors.append(error_msg)
                logger.exception(
                    "[Runtime:%s] Excepción en agente %s", self.mission_id, agent.name
                )
                await self._bus.publish(
                    AgentFailed(
                        mission_id=self.mission_id,
                        agent_id=agent.id,
                        agent_name=agent.name,
                        error=str(exc),
                    )
                )
                self._append_timeline(f"[ERROR] {agent.name} — {exc}")

            finally:
                self._persist()

        # ── Finalizar ──
        if not self._cancellation.is_cancelled:
            self._compute_progress(agents)
            await self._complete()

        self.mission.current_agent = None
        self._persist()

    async def _complete(self) -> None:
        await self._transition(MissionStatus.COMPLETED)
        await self._bus.publish(
            MissionCompleted(
                mission_id=self.mission_id,
                progress=self.mission.progress,
            )
        )
        self._append_timeline(
            f"[COMPLETED] Misión finalizada — {self.mission.progress}%"
        )
        self._persist_event(
            MissionEventType.MISSION_COMPLETED, "Misión completada exitosamente."
        )

    async def _fail(self, reason: str) -> None:
        await self._transition(MissionStatus.FAILED)
        await self._bus.publish(MissionFailed(mission_id=self.mission_id, error=reason))
        self._append_timeline(f"[FAILED] {reason}")
        self._persist()

    # ─────────────────────────────────────────────
    # FSM — Transición de Estado
    # ─────────────────────────────────────────────

    async def _transition(self, new_state: MissionStatus) -> None:
        current = self.mission.status
        if not can_transition_status(current, new_state):
            logger.warning(
                "[Runtime:%s] Transición inválida: %s → %s",
                self.mission_id,
                current,
                new_state,
            )
            return
        logger.info("[Runtime:%s] Estado: %s → %s", self.mission_id, current, new_state)
        self.mission.status = new_state

    # ─────────────────────────────────────────────
    # Helpers internos
    # ─────────────────────────────────────────────

    def _build_context(self) -> AgentContext:
        """Reconstruye el AgentContext desde la SharedMemory persistida de la Misión."""
        events = self._event_repo.get_by_mission(self.mission_id)
        completed = [e.type.value for e in events]
        return AgentContext(
            mission=self.mission,
            shared_memory=SharedMemory(self.mission.metadata.get("shared_memory", {})),
            history=MissionHistory(
                completed_stages=completed,
                current_stage="starting",
                total_events=len(events),
            ),
            current_step=self.mission.current_step.value,
            recommendations=self.mission.metadata.get("recommendations", []),
            events=[],
        )

    def _compute_progress(self, agents: list) -> None:
        executed = [a for a in agents if a.get_status() in ("completed", "error")]
        if executed:
            self.mission.progress = int(
                sum(a.get_progress() for a in executed) / len(executed)
            )

    def _append_timeline(self, entry: str) -> None:
        """El Runtime construye la Timeline — los agentes no la escriben directamente."""
        timestamp = datetime.utcnow().isoformat()
        self.mission.timeline.append(f"{timestamp} | {entry}")

    async def _heartbeat(self) -> None:
        self.mission.last_heartbeat = datetime.utcnow()
        await self._bus.publish(
            RuntimeHeartbeat(
                mission_id=self.mission_id,
                current_agent=self.mission.current_agent,
                progress=self.mission.progress,
                state=self.mission.status.value,
            )
        )

    def _resolve_runtime_start_state(self) -> MissionStatus:
        current = self.mission.status
        if current in {MissionStatus.CREATED, MissionStatus.UPLOADING}:
            return MissionStatus.QUEUED
        if current in {
            MissionStatus.STORED,
            MissionStatus.QUEUED,
            MissionStatus.PAUSED,
            MissionStatus.WAITING_AGENT,
        }:
            return MissionStatus.PROCESSING
        return current

    def _persist(self) -> None:
        self.mission.updated_at = datetime.utcnow()
        self._repo.save(self.mission)

    def _persist_event(self, event_type: MissionEventType, details: str) -> None:
        event = MissionEvent(
            mission_id=self.mission_id,
            source="MissionRuntime",
            type=event_type,
            title="System Event",
            description=details,
        )
        self._event_repo.save(event)
