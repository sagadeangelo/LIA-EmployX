"""
===============================================================
LIA EmployX

DOCX Reader

Extrae texto y metadatos desde archivos Microsoft Word.

Autor:
LIA EmployX Team
===============================================================
"""

from __future__ import annotations

import time
from pathlib import Path

from docx import Document

from backend.modules.cv.engine.document_content import DocumentContent
from backend.modules.cv.engine.readers.base_reader import BaseReader
from backend.modules.cv.loader.docx_loader import DOCXLoader


class DOCXReader(BaseReader):
    """
    Reader especializado para documentos Word (.docx).
    """

    @property
    def supported_extensions(self) -> list[str]:
        return [".docx"]

    # ---------------------------------------------------------

    def read(self, file_path) -> DocumentContent:

        self.validate(file_path)

        file_path = Path(file_path)

        start = time.time()

        document = Document(file_path)

        content = self.create_document(file_path)

        content.mime_type = (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

        content.extracted_by = "python-docx"

        # =====================================================
        # Texto
        # =====================================================

        # Delegate text extraction to the single permanent DOCX ingestion
        # engine; this legacy reader remains an adapter for DocumentContent.
        content.text = DOCXLoader().load(file_path)

        # =====================================================
        # Estadísticas
        # =====================================================

        content.pages = 1

        # =====================================================
        # Metadatos
        # =====================================================

        props = document.core_properties

        content.author = props.author or ""

        content.title = props.title or ""

        content.subject = props.subject or ""

        content.creator = props.author or ""

        if props.keywords:

            content.keywords = [

                k.strip()

                for k in props.keywords.split(",")

                if k.strip()

            ]

        if props.created:

            content.creation_date = str(props.created)

        if props.modified:

            content.modified_date = str(props.modified)

        content.extraction_time = round(

            time.time() - start,

            3

        )

        return content

    # ---------------------------------------------------------

    def __repr__(self):

        return "DOCXReader()"


# ===========================================================
# Prueba local
# ===========================================================

if __name__ == "__main__":

    reader = DOCXReader()

    print(reader)
