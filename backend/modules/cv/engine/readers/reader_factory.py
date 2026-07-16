"""
===============================================================
LIA EmployX

Smart CV Engine

Reader Factory

Responsable de devolver el Reader adecuado según el tipo
de documento.
===============================================================
"""

from .readers.pdf_reader import PDFReader
from .readers.docx_reader import DocxReader
from .readers.image_reader import ImageReader


class ReaderFactory:
    """
    Factory del Smart CV Engine.

    Devuelve la implementación correcta de BaseReader.
    """

    _READERS = {
        "pdf": PDFReader,
        "docx": DocxReader,
        "image": ImageReader,
    }

    @classmethod
    def create(cls, file_type: str):

        file_type = file_type.lower()

        reader_class = cls._READERS.get(file_type)

        if reader_class is None:

            supported = ", ".join(cls._READERS.keys())

            raise ValueError(
                f"No existe un Reader para '{file_type}'. "
                f"Tipos soportados: {supported}"
            )

        return reader_class()

    @classmethod
    def supported_types(cls):

        return list(cls._READERS.keys())


# ===============================================================
# Prueba
# ===============================================================

if __name__ == "__main__":

    print("Readers disponibles:")

    for reader in ReaderFactory.supported_types():
        print(f"  • {reader}")

    pdf_reader = ReaderFactory.create("pdf")

    print()

    print("Reader creado:")

    print(pdf_reader.__class__.__name__)