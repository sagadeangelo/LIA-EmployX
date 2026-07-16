"""
===============================================================
LIA EmployX

BaseAgent

Todos los especialistas heredan de esta clase.
===============================================================
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum


# ===============================================================
# Estados del agente
# ===============================================================

class AgentStatus(Enum):

    CREATED = "created"

    INITIALIZED = "initialized"

    RUNNING = "running"

    PAUSED = "paused"

    STOPPED = "stopped"

    ERROR = "error"


# ===============================================================
# Clase Base
# ===============================================================

class BaseAgent(ABC):

    def __init__(

        self,

        name: str,

        description: str,

        version: str = "1.0.0"

    ):

        self.name = name

        self.description = description

        self.version = version

        self.status = AgentStatus.CREATED

        self.context = None

        self.memory = {}

        self.created_at = datetime.now()

    # ----------------------------------------------------------

    def initialize(self, context):

        self.context = context

        self.status = AgentStatus.INITIALIZED

        self.log("Inicializado.")

    # ----------------------------------------------------------

    @abstractmethod
    def run(self):

        """
        Método principal del especialista.
        """
        pass

    # ----------------------------------------------------------

    def pause(self):

        self.status = AgentStatus.PAUSED

        self.log("Pausado.")

    # ----------------------------------------------------------

    def stop(self):

        self.status = AgentStatus.STOPPED

        self.log("Detenido.")

    # ----------------------------------------------------------

    def resume(self):

        self.status = AgentStatus.RUNNING

        self.log("Reanudado.")

    # ----------------------------------------------------------

    def save_memory(self, key, value):

        self.memory[key] = value

    # ----------------------------------------------------------

    def load_memory(self, key, default=None):

        return self.memory.get(key, default)

    # ----------------------------------------------------------

    def emit_event(self, event_name):

        print(f"[EVENT] {self.name} -> {event_name}")

    # ----------------------------------------------------------

    def receive_event(self, event_name):

        self.log(f"Evento recibido: {event_name}")

    # ----------------------------------------------------------

    def log(self, message):

        print(f"[{self.name}] {message}")

    # ----------------------------------------------------------

    def info(self):

        return {

            "name": self.name,

            "description": self.description,

            "version": self.version,

            "status": self.status.value,

        }
