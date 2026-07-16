"""
===============================================================
LIA EmployX

Certification

Entidad de dominio que representa una certificación
profesional del candidato.

Autor:
LIA EmployX Team
===============================================================
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Certification:
    """
    Representa una certificación profesional.
    """

    name: str = ""

    issuer: str = ""

    issue_date: str = ""

    expiration_date: str = ""

    credential_id: str = ""

    credential_url: str = ""

    description: str = ""

    confidence: float = 1.0

    # ---------------------------------------------------------

    @property
    def is_expired(self) -> bool:
        """
        Placeholder para futura validación de expiración.
        """
        return False

    # ---------------------------------------------------------

    def to_dict(self) -> dict:
        return self.__dict__

    # ---------------------------------------------------------

    def summary(self) -> str:
        return (
            f"{self.name} "
            f"({self.issuer})"
        )