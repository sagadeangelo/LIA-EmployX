"""
===============================================================
LIA EmployX

LLM Request

Representa una solicitud enviada al AI Core.
===============================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class LLMRequest:

    # ---------------------------------------------------------
    # Información de la solicitud
    # ---------------------------------------------------------

    task: str

    prompt: str

    system_prompt: str = ""

    model: str = ""

    provider: str = ""

    # ---------------------------------------------------------
    # Parámetros
    # ---------------------------------------------------------

    temperature: float = 0.20

    top_p: float = 0.95

    max_tokens: int = 4096

    stream: bool = False

    # ---------------------------------------------------------
    # Metadata
    # ---------------------------------------------------------

    created_at: datetime = field(

        default_factory=datetime.utcnow

    )

    metadata: dict = field(

        default_factory=dict

    )

    # ---------------------------------------------------------

    def to_dict(self):

        return {

            "task": self.task,

            "prompt": self.prompt,

            "system_prompt": self.system_prompt,

            "model": self.model,

            "provider": self.provider,

            "temperature": self.temperature,

            "top_p": self.top_p,

            "max_tokens": self.max_tokens,

            "stream": self.stream,

            "created_at": self.created_at.isoformat(),

            "metadata": self.metadata

        }

    # ---------------------------------------------------------

    def summary(self):

        return {

            "task": self.task,

            "provider": self.provider,

            "model": self.model

        }