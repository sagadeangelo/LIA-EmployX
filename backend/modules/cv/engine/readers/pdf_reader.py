"""
===============================================================
LIA EmployX

PDF Reader

Extrae texto y metadatos desde archivos PDF.

Utiliza PyMuPDF (fitz)

Autor:
LIA EmployX Team
===============================================================
"""

from __future__ import annotations

import time
from pathlib import Path

import fitz

from backend.modules.cv.engine.document_content import DocumentContent


class PDFReader:

    """
    Reader especializado para archivos PDF.
    """

    def read(self, file_path) -> DocumentContent:

        file_path = Path(file_path)

        start = time.time()

        doc = fitz.open(file_path)

        content = DocumentContent.from_file(file_path)

        content.mime_type = "application/pdf"

        content.pages = len(doc)

        content.extracted_by = "PyMuPDF"

        # ==========================================
        # Texto
        # ==========================================

        text = []

        for page in doc:

            page_text = page.get_text("text")

            if page_text:

                text.append(page_text)

        content.text = "\n".join(text)

        # ==========================================
        # Metadata
        # ==========================================

        metadata = doc.metadata

        content.author = metadata.get("author", "")

        content.title = metadata.get("title", "")

        content.subject = metadata.get("subject", "")

        content.creator = metadata.get("creator", "")

        content.producer = metadata.get("producer", "")

        content.creation_date = metadata.get("creationDate", "")

        content.modified_date = metadata.get("modDate", "")

        content.extraction_time = round(

            time.time() - start,

            3

        )

        doc.close()

        return content

    # ---------------------------------------------------------

    @property
    def supported_extensions(self):

        return [".pdf"]

    # ---------------------------------------------------------

    def can_read(self, file_path):

        return Path(file_path).suffix.lower() == ".pdf"