from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path


class BaseLoader(ABC):
    """
    Clase base para cualquier lector de documentos.

    Responsabilidad única: convertir un archivo físico en texto plano.
    La construcción del CVDocument y CVMetadata es responsabilidad
    del ExtractionService, no del loader.
    """

    @abstractmethod
    def load(self, file_path: str | Path) -> str:
        """Extrae y retorna el texto crudo del documento."""
        raise NotImplementedError