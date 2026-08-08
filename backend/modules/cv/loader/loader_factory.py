from pathlib import Path

from backend.modules.cv.loader.docx_loader import DOCXLoader
from backend.modules.cv.loader.pdf_loader import PDFLoader


class LoaderFactory:
    """
    Devuelve automáticamente el lector correcto
    según la extensión del archivo.
    """

    @staticmethod
    def get_loader(file_path: str | Path):

        extension = Path(file_path).suffix.lower()

        if extension == ".pdf":
            return PDFLoader()

        if extension == ".docx":
            return DOCXLoader()

        raise ValueError(
            f"Unsupported file type: {extension}"
        )