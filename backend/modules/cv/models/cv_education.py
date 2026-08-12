from __future__ import annotations

from datetime import date

from pydantic import BaseModel


class CVEducation(BaseModel):
    """
    Representa un registro académico detectado en el CV.
    """

    institution: str

    degree: str

    field_of_study: str | None = None

    education_level: str | None = None
    """
    Ejemplos:
    - High School
    - Associate
    - Bachelor's
    - Master's
    - MBA
    - PhD
    - Bootcamp
    - Certification
    """

    location: str | None = None

    start_date: date | None = None

    end_date: date | None = None

    current: bool = False

    description: str | None = None

    gpa: float | None = None

    honors: list[str] = []

    confidence: float = 1.0