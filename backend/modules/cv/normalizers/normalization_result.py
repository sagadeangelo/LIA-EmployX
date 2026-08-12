from dataclasses import dataclass, field
from typing import TypeVar, Generic

T = TypeVar('T')

@dataclass
class NormalizationResult(Generic[T]):
    """
    Contiene el dato normalizado y estructurado, junto con advertencias
    de baja confianza sobre la normalización.
    """
    data: T
    confidence: float = 100.0
    warnings: list[str] = field(default_factory=list)
