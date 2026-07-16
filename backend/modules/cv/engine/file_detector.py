"""
=========================================================
Smart CV Engine

file_detector.py

Detecta el tipo de documento recibido.
=========================================================
"""

from pathlib import Path


class FileDetector:

    PDF = "pdf"

    DOCX = "docx"

    IMAGE = "image"

    UNKNOWN = "unknown"

    IMAGE_EXTENSIONS = {
        ".png",
        ".jpg",
        ".jpeg",
        ".bmp",
        ".tiff",
        ".webp",
        ".heic"
    }

    def detect(self, file_path: str) -> str:

        path = Path(file_path)

        extension = path.suffix.lower()

        if extension == ".pdf":
            return self.PDF

        if extension == ".docx":
            return self.DOCX

        if extension in self.IMAGE_EXTENSIONS:
            return self.IMAGE

        return self.UNKNOWN


if __name__ == "__main__":

    detector = FileDetector()

    print(detector.detect("cv.pdf"))

    print(detector.detect("cv.docx"))

    print(detector.detect("foto.jpg"))

    print(detector.detect("archivo.zip"))