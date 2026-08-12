"""
LIA EmployX — Mission Runtime
Layer 2: RuntimeEvents (Typed Domain Events)

Cada transición del Runtime genera un evento tipado.
El EventBus los distribuye — nadie usa print() para comunicar estado.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional

from backend.runtime.mission_state import MissionStatus


@dataclass(frozen=True)
class RuntimeEvent:
    """Base para todos los eventos del Runtime."""

    mission_id: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def event_type(self) -> str:
        return self.__class__.__name__


# ─────────────────────────────────────────────
# Ciclo de vida de la Misión
# ─────────────────────────────────────────────


@dataclass(frozen=True)
class MissionCreated(RuntimeEvent):
    title: str = ""
    career_goal: str = ""


@dataclass(frozen=True)
class MissionQueued(RuntimeEvent):
    pass


@dataclass(frozen=True)
class MissionStarted(RuntimeEvent):
    pass


@dataclass(frozen=True)
class MissionPaused(RuntimeEvent):
    reason: str = ""


@dataclass(frozen=True)
class MissionResumed(RuntimeEvent):
    pass


@dataclass(frozen=True)
class MissionRecovered(RuntimeEvent):
    """Emitido cuando el Recovery Engine restaura una misión interrumpida."""

    previous_state: str = ""


@dataclass(frozen=True)
class MissionCompleted(RuntimeEvent):
    progress: int = 100


@dataclass(frozen=True)
class MissionFailed(RuntimeEvent):
    error: str = ""


@dataclass(frozen=True)
class MissionCancelled(RuntimeEvent):
    reason: str = "User requested"


# ─────────────────────────────────────────────
# Ciclo de vida del Agente dentro de la Misión
# ─────────────────────────────────────────────


@dataclass(frozen=True)
class AgentStarted(RuntimeEvent):
    agent_id: str = ""
    agent_name: str = ""


@dataclass(frozen=True)
class AgentCompleted(RuntimeEvent):
    agent_id: str = ""
    agent_name: str = ""
    progress: int = 0


@dataclass(frozen=True)
class AgentSkipped(RuntimeEvent):
    agent_id: str = ""
    agent_name: str = ""
    reason: str = ""


@dataclass(frozen=True)
class AgentFailed(RuntimeEvent):
    agent_id: str = ""
    agent_name: str = ""
    error: str = ""


# ─────────────────────────────────────────────
# Heartbeat
# ─────────────────────────────────────────────


@dataclass(frozen=True)
class RuntimeHeartbeat(RuntimeEvent):
    current_agent: Optional[str] = None
    progress: int = 0
    state: str = MissionStatus.PROCESSING.value
