"""
LIA EmployX — Agent Collaboration Engine
Layer 2: AgentContext (Inmutable)

El AgentContext es el único objeto que un agente recibe.
Encapsula todo lo que necesita para trabajar sin consultar repositorios.

INMUTABILIDAD: Los agentes NO modifican el contexto.
Devuelven AgentResult, y el MissionController aplica los cambios.
Esto hace el flujo reproducible, testeable y libre de efectos secundarios.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

from backend.modules.mission.models import Mission, MissionEvent
from backend.agents.base.shared_memory import SharedMemory, SharedMemoryKey


@dataclass(frozen=False)  # Mutable internamente solo para MissionController
class JobProfile:
    """Perfil de vacante de interés."""

    title: str
    company: str
    location: str
    remote: bool
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    required_skills: List[str] = field(default_factory=list)
    description: str = ""
    url: str = ""
    match_score: float = 0.0


@dataclass(frozen=False)
class MissionHistory:
    """Historial de la misión: pasos completados y pendientes."""

    completed_stages: List[str] = field(default_factory=list)
    pending_stages: List[str] = field(default_factory=list)
    current_stage: str = "not_started"
    total_events: int = 0


@dataclass(frozen=False)
class AgentContext:
    """
    Contexto unificado que recibe cada agente.
    Los agentes lo leen pero nunca lo modifican directamente.

    Solo el MissionController lo construye y lo actualiza entre agentes.
    """

    mission: Mission
    history: MissionHistory
    current_step: str
    shared_memory: SharedMemory = field(default_factory=SharedMemory)

    # Documentos de dominio
    job_profile: Optional[JobProfile] = None

    # Acumulados de la sesión actual
    recommendations: List[str] = field(default_factory=list)
    events: List[MissionEvent] = field(default_factory=list)

    def with_memory_updates(self, updates: Dict) -> "AgentContext":
        """
        Devuelve un NUEVO AgentContext con el state actualizado.
        El MissionController lo usa para propagar los resultados de un agente
        al siguiente sin mutar el contexto original.
        """
        new_mission = self.mission.model_copy(deep=True)
        new_shared_memory = SharedMemory(self.shared_memory.snapshot())

        for key, value in updates.items():
            if hasattr(new_mission.state, key):
                setattr(new_mission.state, key, value)
                if key == "profile_id":
                    new_mission.profile_id = value
            elif isinstance(key, SharedMemoryKey):
                new_shared_memory.put(key, value)

        return AgentContext(
            mission=new_mission,
            history=self.history,
            current_step=self.current_step,
            shared_memory=new_shared_memory,
            job_profile=self.job_profile,
            recommendations=list(self.recommendations),
            events=list(self.events),
        )
