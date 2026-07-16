"""
===============================================================
LIA EmployX

Smart CV Engine

Motor principal para lectura de documentos.

Responsabilidades:

• Detectar el tipo de archivo
• Seleccionar el Reader adecuado
• Extraer el contenido
• Devolver un DocumentContent

Autor:
LIA EmployX Team
===============================================================
"""

from __future__ import annotations

from pathlib import Path

from backend.modules.cv.engine.reader_factory import ReaderFactory
from backend.modules.cv.engine.document_content import DocumentContent


class SmartCVEngine:
    """
    Motor principal del sistema de lectura de CV.
    """

    def __init__(self):

        self.factory = ReaderFactory()

    # ---------------------------------------------------------

    def read(self, file_path) -> DocumentContent:
        """
        Lee cualquier documento soportado.

        Parameters
        ----------
        file_path : str | Path

        Returns
        -------
        DocumentContent
        """

        # -----------------------------------------------------
        # Normalizar ruta
        # -----------------------------------------------------

        file_path = Path(
            str(file_path).strip().strip('"').strip("'")
        ).expanduser()

        if not file_path.exists():

            raise FileNotFoundError(
                f"No existe el archivo:\n{file_path}"
            )

        if not self.factory.can_read(file_path):

            raise ValueError(
                f"Formato no soportado: {file_path.suffix}"
            )

        reader = self.factory.get_reader(file_path)

        print()

        print("=" * 70)
        print("Smart CV Engine")
        print("=" * 70)

        print(f"Reader      : {reader.__class__.__name__}")
        print(f"Archivo     : {file_path.name}")
        print(f"Ruta        : {file_path}")

        print()

        content = reader.read(file_path)

        if not isinstance(content, DocumentContent):

            raise TypeError(
                "El Reader debe devolver un DocumentContent."
            )

        return content

    # ---------------------------------------------------------

    def supported_extensions(self):

        return self.factory.supported_extensions()

    # ---------------------------------------------------------

    def can_read(self, file_path) -> bool:

        file_path = Path(
            str(file_path).strip().strip('"').strip("'")
        )

        return self.factory.can_read(file_path)

    # ---------------------------------------------------------

    def print_supported_formats(self):

        print()

        print("=" * 70)
        print("Smart CV Engine")
        print("=" * 70)

        for ext in self.supported_extensions():

            print(f"✓ {ext}")

        print()

    # ---------------------------------------------------------

    def info(self):

        return {

            "engine": "SmartCVEngine",

            "supported_formats": self.supported_extensions(),

            "total_formats": len(self.supported_extensions())

        }


# ===========================================================
# Prueba local
# ===========================================================

if __name__ == "__main__":

    engine = SmartCVEngine()

    engine.print_supported_formats()

    print(engine.info())