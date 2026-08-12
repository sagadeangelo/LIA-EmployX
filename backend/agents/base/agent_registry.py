"""
LIA EmployX — Agent Collaboration Engine
Layer 6: AgentRegistry (Con soporte para plugins)

Registro central de agentes. El MissionController nunca instancia agentes
directamente; siempre los obtiene del registry.

Soporta metadatos de plugin para que en el futuro el Agent Hub pueda
instalar/desinstalar agentes dinámicamente sin modificar el controlador.
"""
from __future__ import annotations

from typing import Dict, List, Optional

from backend.agents.base.base_agent import BaseAgent, AgentMetadata


class AgentRegistry:
    """
    Registro central de agentes del sistema.
    
    Funciona como el catálogo de plugins:
    - Los agentes se registran con sus metadatos.
    - El MissionController consulta qué agentes ejecutar.
    - El Agent Hub puede instalar/desinstalar agentes en runtime.
    """

    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent) -> None:
        """
        Registra un agente en el sistema.
        Si ya existe un agente con el mismo ID, lo reemplaza (permite actualizar versiones).
        """
        if agent.id in self._agents:
            existing = self._agents[agent.id]
            print(f"[Registry] Reemplazando agente '{agent.name}' "
                  f"v{existing.metadata.version} → v{agent.metadata.version}")
        self._agents[agent.id] = agent
        print(f"[Registry] Registrado: {agent.name} v{agent.metadata.version} "
              f"(prioridad: {agent.metadata.priority})")

    def unregister(self, agent_id: str) -> None:
        """Elimina un agente del registry (desinstalación desde Agent Hub)."""
        if agent_id in self._agents:
            removed = self._agents.pop(agent_id)
            print(f"[Registry] Eliminado: {removed.name}")
        else:
            print(f"[Registry] No se encontró agente con ID: {agent_id}")

    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Obtiene un agente por su ID."""
        return self._agents.get(agent_id)

    def get_all_agents(self) -> List[BaseAgent]:
        """
        Devuelve todos los agentes habilitados, ordenados por prioridad.
        Menor número de prioridad = ejecuta primero.
        """
        enabled = [a for a in self._agents.values() if a.metadata.enabled]
        return sorted(enabled, key=lambda a: a.metadata.priority)

    def get_capabilities(self) -> List[str]:
        """Devuelve la lista de todas las capacidades instaladas en el sistema."""
        caps = set()
        for agent in self._agents.values():
            if agent.metadata.enabled:
                caps.update(agent.metadata.capabilities)
        return sorted(list(caps))

    def get_catalog(self) -> List[AgentMetadata]:
        """
        Devuelve los metadatos de todos los agentes registrados.
        Usado por el Agent Hub para mostrar el catálogo.
        """
        return [a.metadata for a in self._agents.values()]

    def enable(self, agent_id: str) -> None:
        """Habilita un agente deshabilitado."""
        if agent_id in self._agents:
            self._agents[agent_id].metadata.enabled = True

    def disable(self, agent_id: str) -> None:
        """Deshabilita un agente sin eliminarlo del registry."""
        if agent_id in self._agents:
            self._agents[agent_id].metadata.enabled = False

    def __len__(self) -> int:
        return len(self._agents)

    def __repr__(self) -> str:
        names = [a.name for a in self.get_all_agents()]
        return f"AgentRegistry({len(self._agents)} agents: {names})"
