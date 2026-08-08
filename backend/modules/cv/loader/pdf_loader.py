from pathlib import Path

import fitz  # PyMuPDF

from backend.modules.cv.loader.base_loader import BaseLoader


class PDFLoader(BaseLoader):
    """
    Extrae texto de archivos PDF utilizando PyMuPDF.
    Responsabilidad única: leer el archivo y retornar texto plano.
    """

    def load(self, file_path: str | Path) -> str:
        file_path = Path(file_path)
        document = fitz.open(file_path)

        pages = [page.get_text() for page in document]
        document.close()

        return "\n".join(pages).strip()