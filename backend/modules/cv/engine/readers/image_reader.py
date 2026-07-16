"""
===============================================================
LIA EmployX

Image Reader

Lee imágenes utilizando OCR (EasyOCR).

Formatos soportados:

    JPG
    JPEG
    PNG
    BMP
    TIFF
    WEBP

Autor:
LIA EmployX Team
===============================================================
"""

from __future__ import annotations

import time
from pathlib import Path

import easyocr

from backend.modules.cv.engine.document_content import DocumentContent
from backend.modules.cv.engine.readers.base_reader import BaseReader


class ImageReader(BaseReader):

    """
    Reader para imágenes usando OCR.
    """

    def __init__(self):

        self.reader = easyocr.Reader(

            ["es", "en"],

            gpu=False

        )

    # ---------------------------------------------------------

    @property
    def supported_extensions(self):

        return [

            ".jpg",

            ".jpeg",

            ".png",

            ".bmp",

            ".tif",

            ".tiff",

            ".webp"

        ]

    # ---------------------------------------------------------

    def read(self, file_path):

        self.validate(file_path)

        file_path = Path(file_path)

        start = time.time()

        content = self.create_document(file_path)

        content.mime_type = "image"

        content.ocr_used = True

        content.extracted_by = "EasyOCR"

        # ==========================================
        # OCR
        # ==========================================

        result = self.reader.readtext(

            str(file_path),

            detail=1

        )

        text = []

        confidences = []

        for item in result:

            bbox, detected_text, confidence = item

            text.append(detected_text)

            confidences.append(confidence)

        content.text = "\n".join(text)

        if confidences:

            content.confidence = round(

                sum(confidences) / len(confidences),

                3

            )

        content.pages = 1

        content.extraction_time = round(

            time.time() - start,

            3

        )

        return content

    # ---------------------------------------------------------

    def __repr__(self):

        return "ImageReader()"


# ===========================================================
# Prueba local
# ===========================================================

if __name__ == "__main__":

    reader = ImageReader()

    print(reader)