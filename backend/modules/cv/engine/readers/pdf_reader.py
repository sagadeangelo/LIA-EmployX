"""Read text PDFs; image-only and encrypted PDFs require another workflow."""
from pathlib import Path
import fitz
from backend.modules.cv.engine.document_content import DocumentContent


class PDFReader:
    supported_extensions = [".pdf"]

    def read(self, file_path):
        content = DocumentContent.from_file(Path(file_path))
        try:
            with fitz.open(file_path) as document:
                if document.needs_pass:
                    raise ValueError("El PDF está protegido con contraseña.")
                content.text = "\n".join(page.get_text("text") for page in document)
                content.pages = len(document)
        except (fitz.FileDataError, RuntimeError) as error:
            raise ValueError("No se pudo leer el PDF. Comprueba que no esté dañado.") from error
        content.mime_type = "application/pdf"
        content.extracted_by = "PyMuPDF"
        return content

    def can_read(self, file_path):
        return Path(file_path).suffix.lower() == ".pdf"
