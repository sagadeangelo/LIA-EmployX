"""
LIA EmployX — Agent Collaboration Engine
Layer 4: LLMProvider (Abstracción Estable)

Interfaz completa para integración con cualquier LLM.
En Fase 3 usamos MockLLMProvider (determinista, sin costo, sin latencia).
En fases posteriores se conectarán OpenAI, Gemini, Claude, Ollama u otros
sin modificar ningún agente.

La interfaz contempla todos los patrones de uso previstos:
  generate()  → Generación de texto libre
  chat()      → Conversación multi-turno
  classify()  → Clasificación con etiquetas
  summarize() → Resumen de texto largo
  extract()   → Extracción estructurada de entidades
  embed()     → Embeddings para búsqueda semántica
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class LLMMessage:
    """Mensaje en una conversación multi-turno."""
    role: str      # "user" | "assistant" | "system"
    content: str


@dataclass
class LLMConfig:
    """Configuración de la llamada al LLM."""
    temperature: float = 0.7
    max_tokens: int = 2048
    model: Optional[str] = None    # Permite forzar un modelo específico
    json_mode: bool = False        # Si True, la respuesta debe ser JSON válido


class LLMProvider(ABC):
    """
    Interfaz estable para cualquier proveedor de IA.
    Todos los agentes dependen de esta abstracción, nunca de una implementación concreta.
    """

    @abstractmethod
    async def generate(self, prompt: str, config: Optional[LLMConfig] = None) -> str:
        """Genera texto a partir de un prompt."""
        ...

    @abstractmethod
    async def chat(
        self,
        messages: List[LLMMessage],
        config: Optional[LLMConfig] = None
    ) -> str:
        """Conversación multi-turno. Devuelve la respuesta del asistente."""
        ...

    @abstractmethod
    async def classify(
        self,
        text: str,
        labels: List[str],
        config: Optional[LLMConfig] = None
    ) -> str:
        """Clasifica el texto dentro de las etiquetas dadas."""
        ...

    @abstractmethod
    async def summarize(self, text: str, config: Optional[LLMConfig] = None) -> str:
        """Resume texto largo en puntos clave."""
        ...

    @abstractmethod
    async def extract(
        self,
        text: str,
        schema: Dict[str, Any],
        config: Optional[LLMConfig] = None
    ) -> Dict[str, Any]:
        """Extrae entidades estructuradas siguiendo el schema dado."""
        ...

    @abstractmethod
    async def embed(self, text: str) -> List[float]:
        """Genera un vector de embeddings para búsqueda semántica."""
        ...


class MockLLMProvider(LLMProvider):
    """
    Implementación determinista para Fase 3.
    Sin costo, sin latencia, sin dependencias externas.
    Permite desarrollar y testear el motor completo antes de conectar LLMs reales.
    """

    async def generate(self, prompt: str, config: Optional[LLMConfig] = None) -> str:
        return f"[MOCK] Respuesta generada para: {prompt[:80]}..."

    async def chat(self, messages: List[LLMMessage], config: Optional[LLMConfig] = None) -> str:
        last = messages[-1].content if messages else ""
        return f"[MOCK] Respuesta de chat para: {last[:80]}..."

    async def classify(self, text: str, labels: List[str], config: Optional[LLMConfig] = None) -> str:
        # Devuelve la primera etiqueta como clasificación mock
        return labels[0] if labels else "unknown"

    async def summarize(self, text: str, config: Optional[LLMConfig] = None) -> str:
        words = text.split()
        return " ".join(words[:30]) + "..." if len(words) > 30 else text

    async def extract(self, text: str, schema: Dict[str, Any], config: Optional[LLMConfig] = None) -> Dict[str, Any]:
        # Devuelve el schema con valores mock basados en el tipo esperado
        result = {}
        for key, hint in schema.items():
            if hint == "list":
                result[key] = ["item_mock_1", "item_mock_2"]
            elif hint == "int":
                result[key] = 75
            elif hint == "float":
                result[key] = 0.75
            elif hint == "bool":
                result[key] = True
            else:
                result[key] = f"mock_{key}"
        return result

    async def embed(self, text: str) -> List[float]:
        # Vector de dimensión 384 (similar a sentence-transformers)
        import hashlib
        seed = int(hashlib.md5(text.encode()).hexdigest(), 16) % (10**8)
        import random
        rng = random.Random(seed)
        return [rng.uniform(-1, 1) for _ in range(384)]
