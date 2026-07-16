"""
===============================================================
LIA EmployX

Base Provider

Clase base para cualquier proveedor de IA.

Todos los proveedores (LM Studio, NVIDIA, Ollama,
OpenAI, Gemini, etc.) deben heredar de esta clase.
===============================================================
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseProvider(ABC):

    def __init__(
        self,
        provider_name: str,
        base_url: str,
    ):

        self.provider_name = provider_name
        self.base_url = base_url
        self.connected = False

    # ==========================================================
    # Conexión
    # ==========================================================

    @abstractmethod
    def connect(self) -> bool:
        """
        Conecta con el proveedor.
        """
        raise NotImplementedError

    @abstractmethod
    def disconnect(self):
        """
        Cierra la conexión.
        """
        raise NotImplementedError

    # ==========================================================
    # Estado
    # ==========================================================

    @abstractmethod
    def health(self) -> bool:
        """
        Devuelve True si el proveedor está disponible.
        """
        raise NotImplementedError

    @abstractmethod
    def available_models(self) -> list[str]:
        """
        Devuelve los modelos disponibles.
        """
        raise NotImplementedError

    # ==========================================================
    # Chat
    # ==========================================================

    @abstractmethod
    def chat(
        self,
        model: str,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_tokens: int,
    ):
        """
        Ejecuta una conversación.
        """
        raise NotImplementedError

    # ==========================================================
    # Streaming
    # ==========================================================

    @abstractmethod
    def stream(
        self,
        model: str,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_tokens: int,
    ):
        """
        Conversación en streaming.
        """
        raise NotImplementedError

    # ==========================================================
    # Embeddings
    # ==========================================================

    @abstractmethod
    def embeddings(
        self,
        model: str,
        text: str,
    ) -> Any:
        """
        Genera embeddings.
        """
        raise NotImplementedError

    # ==========================================================
    # Información
    # ==========================================================

    def info(self):

        return {

            "provider": self.provider_name,

            "base_url": self.base_url,

            "connected": self.connected,

        }

    # ==========================================================
    # Representación
    # ==========================================================

    def __repr__(self):

        return (

            f"<{self.__class__.__name__}"

            f" provider='{self.provider_name}'"

            f" connected={self.connected}>"

        )