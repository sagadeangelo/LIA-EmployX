from __future__ import annotations

from datetime import date

from pydantic import BaseModel
from backend.modules.cv.models.partial_date import PartialDate


class CVExperience(BaseModel):
    """
    Representa una experiencia laboral detectada en el CV.
    """

    company: str

    position: str

    location: str | None = None

    employment_type: str | None = None
    """
    Ejemplos:
    - Full Time
    - Part Time
    - Contract
    - Freelance
    - Internship
    """

    start_date: PartialDate | None = None

    end_date: PartialDate | None = None

    is_current: bool = False

    duration_months: int | None = None

    description: str | None = None

    achievements: list[str] = []

    technologies: list[str] = []

    skills: list[str] = []

    confidence: float = 1.0