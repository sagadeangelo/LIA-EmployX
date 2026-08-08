"""
Language Detection Module

Provides language detection services for the
LIA EmployX CV Processing Pipeline.
"""

from .detector_factory import DetectorFactory
from .language_detector import (
    BaseLanguageDetector,
    LanguageDetector,
)
from .language_result import LanguageResult

__all__ = [
    "DetectorFactory",
    "BaseLanguageDetector",
    "LanguageDetector",
    "LanguageResult",
]