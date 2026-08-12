from __future__ import annotations

from abc import ABC, abstractmethod

from langdetect import DetectorFactory, detect_langs

from backend.modules.cv.language.language_result import LanguageResult
from backend.modules.cv.language.supported_languages import (
    DEFAULT_LANGUAGE,
    SUPPORTED_LANGUAGES,
)

# Hace los resultados reproducibles
DetectorFactory.seed = 0


class BaseLanguageDetector(ABC):
    """
    Base interface for every language detector implementation.
    """

    @abstractmethod
    def detect(self, text: str) -> LanguageResult:
        """
        Detect the primary language of a document.
        """
        raise NotImplementedError


class LanguageDetector(BaseLanguageDetector):
    """
    Default language detector based on the langdetect package.
    """

    def detect(self, text: str) -> LanguageResult:
        """
        Detect the primary language of a CV.

        Args:
            text: Plain text extracted from the document.

        Returns:
            LanguageResult
        """

        text = (text or "").strip()

        if len(text) < 20:
            return LanguageResult(
                language="unknown",
                language_name="Unknown",
                confidence=0.0,
                detector="langdetect",
            )

        try:
            predictions = detect_langs(text)

            best = predictions[0]

            language = SUPPORTED_LANGUAGES.get(
                best.lang,
                DEFAULT_LANGUAGE,
            )

            bilingual = False
            secondary_language = None

            if len(predictions) > 1:
                second = predictions[1]

                if second.prob >= 0.20:
                    bilingual = True
                    secondary_language = second.lang

            return LanguageResult(
                language=language.code,
                language_name=language.name,
                confidence=round(best.prob, 4),
                bilingual=bilingual,
                secondary_language=secondary_language,
                detector="langdetect",
            )

        except Exception:
            return LanguageResult(
                language="unknown",
                language_name="Unknown",
                confidence=0.0,
                detector="langdetect",
            )