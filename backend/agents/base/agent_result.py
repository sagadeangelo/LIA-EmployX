"""
LIA EmployX — Agent Collaboration Engine
Layer 3: AgentResult (Acumulativo)

El tipo de retorno estándar para TODOS los agentes.
Ningún agente devuelve objetos arbitrarios.

ACUMULATIVO: Cada agente solo devuelve sus PROPIAS contribuciones.
El MissionController es el único responsable de fusionar:
  - eventos
  - recomendaciones
  - progreso
  - contexto
  - memoria compartida
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from backend.modules.mission.models import Mission, MissionEvent
from backend.agents.base.shared_memory import SharedMemoryKey


@dataclass
class AgentResult:
    """
    Resultado estándar devuelto por todos los agentes.
    
    Contiene SOLO las contribuciones de este agente en esta ejecución.
    El MissionController fusiona los resultados de cada agente en secuencia.
    """
    # Estado de ejecución
    success: bool

    # Progreso de ESTE agente (0-100)
    progress: int

    # Contribuciones de este agente (acumulativas, no sobrescriben)
    recommendations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    events: List[MissionEvent] = field(default_factory=list)

    # Updates a SharedMemory — el MissionController los aplica
    # Usa SharedMemoryKey para garantizar tipado correcto
    memory_updates: Dict[SharedMemoryKey, Any] = field(default_factory=dict)

    # Mission actualizada (solo si cambió algo en la misión misma)
    updated_mission: Optional[Mission] = None

    # Mensaje de error si success=False
    error: Optional[str] = None

    @classmethod
    def failure(cls, error: str, progress: int = 0) -> "AgentResult":
        """Factory para errores. Evita boilerplate."""
        return cls(success=False, progress=progress, error=error)

    @classmethod
    def ok(
        cls,
        progress: int,
        recommendations: List[str] = None,
        memory_updates: Dict[SharedMemoryKey, Any] = None,
        events: List[MissionEvent] = None,
        warnings: List[str] = None,
        updated_mission: Optional[Mission] = None,
    ) -> "AgentResult":
        """Factory para resultados exitosos."""
        return cls(
            success=True,
            progress=progress,
            recommendations=recommendations or [],
            warnings=warnings or [],
            events=events or [],
            memory_updates=memory_updates or {},
            updated_mission=updated_mission,
        )
