"""
===============================================================
LIA EmployX

Document Content

Representa el contenido bruto de cualquier documento
antes de ser analizado por la IA.
===============================================================
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DocumentContent:
    """
    Contenido extraído de un documento.

    Este objeto es generado por los Readers
    (PDFReader, DocxReader, ImageReader, etc.)
    y será consumido por el CVParser.
    """

    # ---------------------------------------------------------
    # Información del archivo
    # ---------------------------------------------------------

    file_name: str = ""

    file_path: str = ""

    file_type: str = ""

    file_size: int = 0

    # ---------------------------------------------------------
    # Información del documento
    # ---------------------------------------------------------

    total_pages: int = 0

    total_images: int = 0

    total_tables: int = 0

    language: str = ""

    encoding: str = "utf-8"

    # ---------------------------------------------------------
    # Contenido extraído
    # ---------------------------------------------------------

    text: str = ""

    # Texto separado por página
    pages: list[str] = field(default_factory=list)

    # Imágenes encontradas
    images: list[Any] = field(default_factory=list)

    # Tablas encontradas
    tables: list[Any] = field(default_factory=list)

    # ---------------------------------------------------------
    # Información adicional
    # ---------------------------------------------------------

    metadata: dict[str, Any] = field(default_factory=dict)

    warnings: list[str] = field(default_factory=list)

    errors: list[str] = field(default_factory=list)

    # ---------------------------------------------------------
    # Utilidades
    # ---------------------------------------------------------

    @property
    def character_count(self) -> int:
        return len(self.text)

    @property
    def word_count(self) -> int:
        return len(self.text.split())

    @property
    def is_empty(self) -> bool:
        return self.character_count == 0

    def add_warning(self, message: str):
        self.warnings.append(message)

    def add_error(self, message: str):
        self.errors.append(message)

    def summary(self) -> dict:
        """
        Devuelve un resumen del documento.
        """

        return {
            "file_name": self.file_name,
            "file_type": self.file_type,
            "pages": self.total_pages,
            "characters": self.character_count,
            "words": self.word_count,
            "images": self.total_images,
            "tables": self.total_tables,
            "warnings": len(self.warnings),
            "errors": len(self.errors),
        }

    def __str__(self):

        return (
            f"DocumentContent("
            f"file='{self.file_name}', "
            f"type='{self.file_type}', "
            f"pages={self.total_pages}, "
            f"characters={self.character_count}, "
            f"words={self.word_count})"
        )