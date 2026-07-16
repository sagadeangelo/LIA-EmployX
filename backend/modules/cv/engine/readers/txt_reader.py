"""
===============================================================
LIA EmployX

TXT Reader

Lee archivos de texto plano (.txt)

Autor:
LIA EmployX Team
===============================================================
"""

from __future__ import annotations

import time
from pathlib import Path

from backend.modules.cv.engine.document_content import DocumentContent
from backend.modules.cv.engine.readers.base_reader import BaseReader


class TXTReader(BaseReader):
    """
    Reader especializado para archivos TXT.
    """

    @property
    def supported_extensions(self) -> list[str]:
        return [".txt"]

    # ---------------------------------------------------------

    def read(self, file_path) -> DocumentContent:

        self.validate(file_path)

        file_path = Path(file_path)

        start = time.time()

        content = self.create_document(file_path)

        content.mime_type = "text/plain"

        content.extracted_by = "TXT Reader"

        # -----------------------------------------------------
        # Intentar varias codificaciones
        # -----------------------------------------------------

        encodings = [

            "utf-8",

            "utf-8-sig",

            "latin-1",

            "cp1252"

        ]

        text = None

        for encoding in encodings:

            try:

                with open(

                    file_path,

                    "r",

                    encoding=encoding

                ) as f:

                    text = f.read()

                content.encoding = encoding

                break

            except UnicodeDecodeError:

                continue

        if text is None:

            raise ValueError(

                f"No fue posible leer el archivo:\n{file_path}"

            )

        content.text = text

        content.pages = 1

        content.language = ""

        content.extraction_time = round(

            time.time() - start,

            3

        )

        return content

    # ---------------------------------------------------------

    def __repr__(self):

        return "TXTReader()"


# ===========================================================
# Prueba local
# ===========================================================

if __name__ == "__main__":

    reader = TXTReader()

    print(reader)

    print(reader.supported_extensions)