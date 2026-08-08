"""
LIA EmployX
CV Loader Package

Este paquete contiene los cargadores de documentos soportados
por el sistema de análisis de CV.

Actualmente soporta:

- PDF
- DOCX

La selección automática del loader se realiza mediante
LoaderFactory.
"""

from .base_loader import BaseLoader
from .pdf_loader import PDFLoader
from .docx_loader import DOCXLoader
from .extraction_models import (
    DocumentExtractionError,
    ExtractionReport,
    ExtractionResult,
    ExtractionStatus,
)
from .loader_factory import LoaderFactory

__all__ = [
    "BaseLoader",
    "PDFLoader",
    "DOCXLoader",
    "DocumentExtractionError",
    "ExtractionReport",
    "ExtractionResult",
    "ExtractionStatus",
    "LoaderFactory",
]
