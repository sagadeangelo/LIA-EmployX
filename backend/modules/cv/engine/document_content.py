"""
===============================================================
LIA EmployX

Document Content

Representa el contenido extraído de un documento.

Todos los Readers (PDF, DOCX, TXT, OCR, etc.)
deben devolver esta entidad.

Autor:
LIA EmployX Team
===============================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime


@dataclass(slots=True)
class DocumentContent:
    """
    Documento extraído por SmartCVEngine.
    """

    # ---------------------------------------------------------
    # Archivo
    # ---------------------------------------------------------

    file_name: str = ""

    file_path: str = ""

    extension: str = ""

    mime_type: str = ""

    file_size: int = 0

    # ---------------------------------------------------------
    # Contenido
    # ---------------------------------------------------------

    text: str = ""

    pages: int = 0

    language: str = ""

    encoding: str = "utf-8"

    # ---------------------------------------------------------
    # Metadatos
    # ---------------------------------------------------------

    author: str = ""

    title: str = ""

    subject: str = ""

    creator: str = ""

    producer: str = ""

    keywords: list[str] = field(default_factory=list)

    creation_date: str = ""

    modified_date: str = ""

    # ---------------------------------------------------------
    # Información técnica
    # ---------------------------------------------------------

    extracted_by: str = ""

    extraction_time: float = 0.0

    ocr_used: bool = False

    confidence: float = 1.0

    # ---------------------------------------------------------
    # Utilidades
    # ---------------------------------------------------------

    @property
    def characters(self) -> int:

        return len(self.text)

    # ---------------------------------------------------------

    @property
    def words(self) -> int:

        return len(self.text.split())

    # ---------------------------------------------------------

    @property
    def lines(self) -> int:

        return len(self.text.splitlines())

    # ---------------------------------------------------------

    @property
    def is_empty(self) -> bool:

        return len(self.text.strip()) == 0

    # ---------------------------------------------------------

    def summary(self) -> dict:

        return {

            "file": self.file_name,

            "extension": self.extension,

            "pages": self.pages,

            "characters": self.characters,

            "words": self.words,

            "language": self.language,

            "ocr_used": self.ocr_used,

            "confidence": self.confidence

        }

    # ---------------------------------------------------------

    @classmethod
    def from_file(cls, file_path: Path):

        file_path = Path(file_path)

        instance = cls()

        instance.file_name = file_path.name

        instance.file_path = str(file_path)

        instance.extension = file_path.suffix.lower()

        if file_path.exists():

            instance.file_size = file_path.stat().st_size

        return instance

    # ---------------------------------------------------------

    def print_summary(self):

        print()

        print("=" * 70)

        print("Document Content")

        print("=" * 70)

        print()

        print(f"Archivo      : {self.file_name}")

        print(f"Extensión    : {self.extension}")

        print(f"Tamaño       : {self.file_size:,} bytes")

        print(f"Páginas      : {self.pages}")

        print(f"Caracteres   : {self.characters:,}")

        print(f"Palabras     : {self.words:,}")

        print(f"Idioma       : {self.language}")

        print(f"OCR          : {self.ocr_used}")

        print(f"Confianza    : {self.confidence}")

        print()

        print("=" * 70)


# ===========================================================
# Prueba local
# ===========================================================

if __name__ == "__main__":

    doc = DocumentContent()

    doc.file_name = "cv.pdf"

    doc.extension = ".pdf"

    doc.text = "Hola mundo\nEste es un CV."

    doc.pages = 1

    doc.language = "es"

    doc.print_summary()