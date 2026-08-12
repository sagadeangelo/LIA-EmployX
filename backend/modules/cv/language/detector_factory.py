from __future__ import annotations

from backend.modules.cv.language.language_detector import (
    BaseLanguageDetector,
    LanguageDetector,
)


class DetectorFactory:
    """
    Factory responsible for providing the active
    language detector implementation.

    This allows changing the detector in the future
    without modifying the rest of the pipeline.

    Supported implementations may include:

        - langdetect
        - lingua
        - fastText
        - NVIDIA NIM
        - Local LLM
    """

    _detector: BaseLanguageDetector | None = None

    @classmethod
    def get_detector(cls) -> BaseLanguageDetector:
        """
        Returns the singleton language detector.
        """

        if cls._detector is None:
            cls._detector = LanguageDetector()

        return cls._detector