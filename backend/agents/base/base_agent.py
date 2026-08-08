"""
LIA EmployX — Agent Collaboration Engine
Layer 5: BaseAgent (Contrato Final)

Todos los agentes del sistema heredan de esta clase.
El contrato garantiza:
 - Recibir AgentContext (inmutable desde su perspectiva)
 - Devolver AgentResult (acumulativo, no destructivo)
 - Declarar metadatos de plugin para el AgentRegistry
 - Usar LLMProvider como abstracción (nunca conectar LLMs directamente)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional

from backend.agents.base.agent_context import AgentContext
from backend.agents.base.agent_result import AgentResult
from backend.agents.llm.llm_provider import LLMProvider


@dataclass
class AgentMetadata:
    """
    Metadatos de plugin para el AgentRegistry.
    Permite instalar/desinstalar agentes dinámicamente desde Agent Hub
    sin modificar el código del MissionController.
    """

    id: str
    name: str
    version: str
    author: str
    description: str
    capabilities: List[str]
    dependencies: List[str] = field(
        default_factory=list
    )  # IDs de agentes que deben ejecutar antes
    priority: int = 50  # 1-100. Los agentes con menor número ejecutan primero.
    enabled: bool = True


class BaseAgent(ABC):
    """
    Clase base del Agent Framework.

    Principios:
    - Solo recibe AgentContext, nunca repositorios ni servicios externos.
    - Solo devuelve AgentResult, nunca objetos arbitrarios.
    - Usa LLMProvider para toda inferencia de IA.
    - Nunca llama a otros agentes directamente.
    - Nunca modifica el estado global.
    """

    def __init__(self, llm: Optional[LLMProvider] = None):
        self._llm = llm
        self._status: str = "created"
        self._progress: int = 0
        self._recommendations: List[str] = []

    @property
    @abstractmethod
    def metadata(self) -> AgentMetadata:
        """
        Declara los metadatos del agente para el AgentRegistry.
        Implementado como property para que sea parte del tipo, no del constructor.
        """
        ...

    @abstractmethod
    async def execute(self, context: AgentContext) -> AgentResult:
        """
        Lógica principal del agente.

        Recibe: AgentContext (solo lectura desde la perspectiva del agente)
        Devuelve: AgentResult con sus contribuciones

        NUNCA modificar context directamente.
        NUNCA llamar a otros agentes.
        NUNCA consultar repositorios.
        """
        ...

    @abstractmethod
    def can_execute(self, context: AgentContext) -> bool:
        """
        Evalúa si las precondiciones se cumplen para ejecutar este agente.
        Verifica existencia de datos en context.shared_memory usando SharedMemoryKey.
        """
        ...

    # -----------------------------------------------------------------
    # Estado público (accedido por MissionController y AgentRegistry)
    # -----------------------------------------------------------------

    def get_status(self) -> str:
        return self._status

    def get_progress(self) -> int:
        return self._progress

    def get_recommendations(self) -> List[str]:
        return list(self._recommendations)

    # Shortcuts para acceso a metadata
    @property
    def id(self) -> str:
        return self.metadata.id

    @property
    def name(self) -> str:
        return self.metadata.name

    @property
    def capabilities(self) -> List[str]:
        return self.metadata.capabilities

    # -----------------------------------------------------------------
    # Helpers internos (para subclases)
    # -----------------------------------------------------------------

    def _set_status(self, status: str) -> None:
        self._status = status

    def _set_progress(self, progress: int) -> None:
        self._progress = max(0, min(100, progress))

    def log(self, message: str) -> None:
        print(f"[{self.metadata.name} v{self.metadata.version}] {message}")
