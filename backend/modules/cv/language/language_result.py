from __future__ import annotations

from pydantic import BaseModel


class LanguageResult(BaseModel):
    """
    Result returned by the language detector.
    """

    language: str
    """
    ISO-639-1 language code.

    Examples:

    es
    en
    fr
    pt
    de
    """

    language_name: str

    confidence: float

    bilingual: bool = False

    secondary_language: str | None = None

    detector: str = "langdetect"