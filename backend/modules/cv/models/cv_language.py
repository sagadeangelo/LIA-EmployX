from __future__ import annotations

from pydantic import BaseModel


class CVLanguage(BaseModel):
    """
    Representa un idioma detectado en el CV.
    """

    name: str
    """
    Ejemplos:
    - English
    - Spanish
    - French
    - German
    """

    level: str | None = None
    """
    Ejemplos:

    A1
    A2
    B1
    B2
    C1
    C2

    Native
    Fluent
    Professional
    Conversational
    """

    native: bool = False

    certified: bool = False

    certification: str | None = None
    """
    Ejemplos:

    TOEFL
    IELTS
    TOEIC
    Cambridge
    """

    score: str | None = None

    confidence: float = 1.0