"""
===============================================================
LIA EmployX

LLM Response

Representa la respuesta de cualquier modelo.

Todos los providers deben devolver esta clase.
===============================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class LLMResponse:

    # ---------------------------------------------------------
    # Resultado
    # ---------------------------------------------------------

    success: bool

    content: str

    # ---------------------------------------------------------
    # Modelo
    # ---------------------------------------------------------

    provider: str

    model: str

    task: str

    # ---------------------------------------------------------
    # Rendimiento
    # ---------------------------------------------------------

    elapsed_seconds: float = 0.0

    # ---------------------------------------------------------
    # Tokens
    # ---------------------------------------------------------

    input_tokens: int = 0

    output_tokens: int = 0

    total_tokens: int = 0

    # ---------------------------------------------------------
    # Información adicional
    # ---------------------------------------------------------

    finish_reason: str = ""

    raw_response: dict = field(

        default_factory=dict

    )

    created_at: datetime = field(

        default_factory=datetime.utcnow

    )

    # ---------------------------------------------------------

    @property
    def token_count(self):

        return self.total_tokens

    # ---------------------------------------------------------

    def to_dict(self):

        return {

            "success": self.success,

            "provider": self.provider,

            "model": self.model,

            "task": self.task,

            "elapsed_seconds": self.elapsed_seconds,

            "input_tokens": self.input_tokens,

            "output_tokens": self.output_tokens,

            "total_tokens": self.total_tokens,

            "finish_reason": self.finish_reason,

            "content": self.content,

            "created_at": self.created_at.isoformat()

        }

    # ---------------------------------------------------------

    def print_summary(self):

        print()

        print("=" * 70)

        print("LIA EmployX AI Response")

        print("=" * 70)

        print()

        print(f"Success      : {self.success}")

        print(f"Provider     : {self.provider}")

        print(f"Model        : {self.model}")

        print(f"Task         : {self.task}")

        print(f"Time         : {self.elapsed_seconds:.2f}s")

        print(f"Tokens       : {self.total_tokens}")

        print()

        print("Content")

        print("-" * 70)

        print(self.content)

        print("-" * 70)