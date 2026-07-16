"""
===============================================================
LIA EmployX

Reader Factory

Selecciona automáticamente el Reader adecuado
según el tipo de archivo.

Autor:
LIA EmployX Team
===============================================================
"""

from __future__ import annotations

from pathlib import Path

from backend.modules.cv.engine.readers.pdf_reader import PDFReader
from backend.modules.cv.engine.readers.docx_reader import DOCXReader
from backend.modules.cv.engine.readers.txt_reader import TXTReader


class ReaderFactory:

    """
    Fábrica de Readers.
    """

    def __init__(self):

        self.readers = {

            ".pdf": PDFReader(),

            ".docx": DOCXReader(),

            ".txt": TXTReader()

        }

    # ---------------------------------------------------------

    def get_reader(self, file_path) -> object:

        """
        Devuelve el Reader correspondiente.
        """

        extension = Path(file_path).suffix.lower()

        if extension not in self.readers:

            raise ValueError(

                f"Formato no soportado: {extension}"

            )

        return self.readers[extension]

    # ---------------------------------------------------------

    def supported_extensions(self):

        return sorted(self.readers.keys())

    # ---------------------------------------------------------

    def can_read(self, file_path):

        extension = Path(file_path).suffix.lower()

        return extension in self.readers

    # ---------------------------------------------------------

    def register(self, extension: str, reader):

        """
        Permite registrar nuevos Readers.
        """

        extension = extension.lower()

        if not extension.startswith("."):

            extension = "." + extension

        self.readers[extension] = reader

    # ---------------------------------------------------------

    def print_readers(self):

        print()

        print("=" * 70)

        print("Readers registrados")

        print("=" * 70)

        print()

        for ext, reader in self.readers.items():

            print(

                f"{ext:<8}"

                f" -> "

                f"{reader.__class__.__name__}"

            )

        print()


# ============================================================
# Prueba local
# ============================================================

if __name__ == "__main__":

    factory = ReaderFactory()

    factory.print_readers()

    print(factory.get_reader("cv.pdf"))

    print(factory.get_reader("cv.docx"))

    print(factory.get_reader("cv.txt"))