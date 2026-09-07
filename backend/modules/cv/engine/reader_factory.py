"""Readers enabled for the first CV flow: text PDF and TXT."""
from pathlib import Path
from backend.modules.cv.engine.readers.pdf_reader import PDFReader
from backend.modules.cv.engine.readers.txt_reader import TXTReader


class ReaderFactory:
    def __init__(self):
        self.readers = {".pdf": PDFReader(), ".txt": TXTReader()}

    def get_reader(self, file_path):
        extension = Path(file_path).suffix.lower()
        if extension not in self.readers:
            raise ValueError("Formato no admitido. Selecciona PDF con texto o TXT.")
        return self.readers[extension]

    def supported_extensions(self):
        return sorted(self.readers)

    def can_read(self, file_path):
        return Path(file_path).suffix.lower() in self.readers

    def register(self, extension, reader):
        self.readers['.' + extension.lower().lstrip('.')] = reader

    @classmethod
    def create(cls, file_type):
        return cls().get_reader('cv.' + file_type.lstrip('.'))
