from pathlib import Path

# ============================================================
# LIA EmployX
# Smart CV Engine
# Crear Readers
# ============================================================

ROOT = Path(
    r"D:\PROYECTOS_FLUTTER\lia-employx\backend\modules\cv\engine\readers"
)

ROOT.mkdir(parents=True, exist_ok=True)

FILES = {

"__init__.py": '''"""
Smart CV Engine Readers
"""
''',

"base_reader.py": '''"""
Clase base para todos los lectores de documentos.
"""

from abc import ABC, abstractmethod


class BaseReader(ABC):

    @abstractmethod
    def read(self, file_path: str) -> str:
        """
        Debe devolver el texto contenido en el documento.
        """
        pass
''',

"pdf_reader.py": '''"""
Lector de archivos PDF.
"""

from .base_reader import BaseReader


class PDFReader(BaseReader):

    def read(self, file_path: str) -> str:

        print(f"Leyendo PDF: {file_path}")

        return ""
''',

"docx_reader.py": '''"""
Lector de archivos DOCX.
"""

from .base_reader import BaseReader


class DocxReader(BaseReader):

    def read(self, file_path: str) -> str:

        print(f"Leyendo DOCX: {file_path}")

        return ""
''',

"image_reader.py": '''"""
Lector de imágenes (OCR).
"""

from .base_reader import BaseReader


class ImageReader(BaseReader):

    def read(self, file_path: str) -> str:

        print(f"Leyendo Imagen: {file_path}")

        return ""
'''

}

print("\n========================================")
print("Creando Readers...")
print("========================================\n")

for filename, content in FILES.items():

    file = ROOT / filename

    file.write_text(content, encoding="utf-8")

    print(f"✓ {filename}")

print("\n========================================")
print("Readers creados correctamente.")
print("========================================")