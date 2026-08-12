from __future__ import annotations

from pydantic import BaseModel, Field


class CVSection(BaseModel):
    """
    Represents a logical section inside a CV.

    Examples
    --------
    - Contact
    - Professional Summary
    - Experience
    - Education
    - Skills
    - Languages
    - Certifications
    """

    name: str
    """
    Canonical section name.

    Example:
        experience
        education
        skills
    """

    title: str
    """
    Original section title found in the document.

    Example:
        EXPERIENCE
        EXPERIENCIA LABORAL
        WORK HISTORY
    """

    content: str = ""

    order: int = 0
    """
    Position inside the document.
    """

    start_index: int | None = None

    end_index: int | None = None

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )

    language: str | None = None

    normalized: bool = False