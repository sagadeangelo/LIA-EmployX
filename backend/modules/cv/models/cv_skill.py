from __future__ import annotations

from pydantic import BaseModel, Field


class CVSkill(BaseModel):
    """
    Representa una habilidad detectada dentro del CV.

    Puede provenir de una sección de Skills,
    Experiencia Laboral, Certificaciones o Proyectos.
    """

    name: str

    category: str | None = None
    """
    Ejemplos:
    - Programming Language
    - Framework
    - Database
    - Cloud
    - DevOps
    - Soft Skill
    - AI
    """

    level: str | None = None
    """
    Ejemplos:
    - Beginner
    - Intermediate
    - Advanced
    - Expert
    """

    years: float | None = None

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )

    source: str | None = None
    """
    Lugar donde fue encontrada.

    Ejemplos:
    - Skills
    - Experience
    - Projects
    - Certifications
    """

    verified: bool = False