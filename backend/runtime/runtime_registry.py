"""
LIA EmployX — Mission Runtime
Layer 5: RuntimeRegistry (Mission ID → MissionRuntime)

El RuntimeRegistry es el kernel table del Career OS:
  - Mapa de todas las misiones activas en memoria
  - Crea, inicia, pausa, cancela y recupera instancias de MissionRuntime
  - Publica heartbeats de todas las misiones activas
  - Es el único punto de entrada para operar sobre una misión en ejecución
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Dict, List, Optional

from backend.agents.bootstrap import build_registry
from backend.modules.mission.models import Mission, MissionEventType
from backend.modules.mission.repositories import (
    MissionRepository,
    MissionEventRepository,
)
from backend.runtime.event_bus import RuntimeEventBus, runtime_bus
from backend.runtime.mission_runtime import MissionRuntime
from backend.runtime.mission_state import MissionStatus

logger = logging.getLogger(__name__)


class RuntimeRegistry:
    """
    Registro central de todas las instancias MissionRuntime activas.

    Uso:
        registry = RuntimeRegistry(mission_repo, event_repo)
        await registry.start_mission(mission)
        await registry.cancel_mission(mission_id)
        info = registry.inspect(mission_id)
    """

    def __init__(
        self,
        mission_repo: MissionRepository,
        event_repo: MissionEventRepository,
        bus: Optional[RuntimeEventBus] = None,
    ) -> None:
        self._mission_repo = mission_repo
        self._event_repo = event_repo
        self._bus = bus or runtime_bus
        self._agent_registry = build_registry()
        self._runtimes: Dict[str, MissionRuntime] = {}

    # ─────────────────────────────────────────────
    # Control de misiones
    # ─────────────────────────────────────────────

    async def start_mission(self, mission: Mission) -> MissionRuntime:
        """Crea una instancia de Runtime y ejecuta la misión en segundo plano."""
        runtime = MissionRuntime(
            mission=mission,
            mission_repo=self._mission_repo,
            event_repo=self._event_repo,
            registry=self._agent_registry,
            bus=self._bus,
        )
        self._runtimes[mission.id] = runtime
        logger.info("[RuntimeRegistry] Iniciando misión: %s", mission.id)

        if mission.status in {MissionStatus.CREATED, MissionStatus.UPLOADING}:
            mission.status = MissionStatus.QUEUED

        import asyncio

        asyncio.create_task(runtime.run())
        return runtime

    async def recover_mission(self, mission: Mission) -> MissionRuntime:
        """Recupera una misión interrumpida y la vuelve a ejecutar."""
        previous_state = mission.status.value
        mission.status = MissionStatus.QUEUED

        runtime = MissionRuntime(
            mission=mission,
            mission_repo=self._mission_repo,
            event_repo=self._event_repo,
            registry=self._agent_registry,
            bus=self._bus,
        )
        self._runtimes[mission.id] = runtime
        logger.info(
            "[RuntimeRegistry] Recuperando misión: %s (era: %s)",
            mission.id,
            previous_state,
        )

        import asyncio

        asyncio.create_task(runtime.recover(previous_state))
        return runtime

    async def cancel_mission(
        self, mission_id: str, reason: str = "User requested"
    ) -> bool:
        """Cancela una misión activa."""
        runtime = self._runtimes.get(mission_id)
        if not runtime:
            logger.warning(
                "[RuntimeRegistry] Misión no encontrada para cancelar: %s", mission_id
            )
            return False
        await runtime.cancel(reason)
        self._runtimes.pop(mission_id, None)
        return True

    async def pause_mission(self, mission_id: str, reason: str = "") -> bool:
        """Pausa una misión activa."""
        runtime = self._runtimes.get(mission_id)
        if not runtime:
            return False
        await runtime.pause(reason)
        return True

    # ─────────────────────────────────────────────
    # Inspección
    # ─────────────────────────────────────────────

    def get_runtime(self, mission_id: str) -> Optional[MissionRuntime]:
        return self._runtimes.get(mission_id)

    def list_active(self) -> List[str]:
        return list(self._runtimes.keys())

    def inspect(self, mission_id: str) -> Optional[dict]:
        runtime = self._runtimes.get(mission_id)
        if not runtime:
            return None
        return {
            "mission_id": mission_id,
            "state": runtime.state.value,
            "current_agent": runtime.current_agent,
            "progress": runtime.mission.progress,
            "execution_seconds": round(runtime.execution_seconds, 2),
            "last_heartbeat": (
                runtime.mission.last_heartbeat.isoformat()
                if runtime.mission.last_heartbeat
                else None
            ),
            "errors": runtime.mission.errors,
        }

    def inspect_all(self) -> List[dict]:
        return [self.inspect(mid) for mid in self._runtimes]

    def __len__(self) -> int:
        return len(self._runtimes)


# ─────────────────────────────────────────────
# Singleton global
# ─────────────────────────────────────────────
# Se inicializa en el lifespan de FastAPI (backend/main.py)
# y se importa donde se necesite:
#   from backend.runtime.runtime_registry import get_runtime_registry

_registry_instance: Optional[RuntimeRegistry] = None


def init_runtime_registry(
    mission_repo: MissionRepository,
    event_repo: MissionEventRepository,
) -> RuntimeRegistry:
    global _registry_instance
    _registry_instance = RuntimeRegistry(mission_repo, event_repo)
    return _registry_instance


def get_runtime_registry() -> RuntimeRegistry:
    if _registry_instance is None:
        raise RuntimeError(
            "RuntimeRegistry no fue inicializado. "
            "Llama a init_runtime_registry() en el lifespan de FastAPI."
        )
    return _registry_instance
