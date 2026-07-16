"""
===============================================================
LIA EmployX
Smart CV Engine

pipeline.py

Orquestador principal del Smart CV Engine.
===============================================================
"""

from pathlib import Path

from backend.modules.cv.engine.file_detector import FileDetector
from backend.modules.cv.engine.readers.reader_factory import ReaderFactory


class SmartCVPipeline:
    """
    Coordina todo el flujo del Smart CV Engine.

        Archivo
           │
           ▼
    FileDetector
           │
           ▼
    ReaderFactory
           │
           ▼
      PDFReader
           │
           ▼
    DocumentContent
           │
           ▼
       CV Parser
           │
           ▼
    ProfessionalProfile
    """

    def __init__(self):

        self.detector = FileDetector()

        print("\n🚀 Smart CV Engine iniciado.\n")

    # ---------------------------------------------------------

    def process(self, file_path: str):

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"\nNo existe el archivo:\n{file_path}"
            )

        print("=" * 80)
        print("                LIA EmployX - Smart CV Engine")
        print("=" * 80)

        print(f"\n📄 Archivo : {path.name}")

        # =====================================================
        # PASO 1
        # =====================================================

        print("\n[1/5] Detectando tipo de archivo...")

        file_type = self.detector.detect(str(path))

        print(f"      ✔ {file_type}")

        # =====================================================
        # PASO 2
        # =====================================================

        print("\n[2/5] Seleccionando Reader...")

        reader = ReaderFactory.create(file_type)

        print(f"      ✔ {reader.__class__.__name__}")

        # =====================================================
        # PASO 3
        # =====================================================

        print("\n[3/5] Leyendo documento...")

        document = reader.read(str(path))

        print(f"      ✔ Páginas     : {document.total_pages}")
        print(f"      ✔ Caracteres  : {document.character_count}")
        print(f"      ✔ Palabras    : {document.word_count}")

        # =====================================================
        # VISTA PREVIA
        # =====================================================

        print("\n" + "=" * 80)
        print("VISTA PREVIA DEL DOCUMENTO")
        print("=" * 80)

        preview = document.text

        if len(preview) > 1500:
            preview = preview[:1500] + "\n\n...(continúa)..."

        print(preview)

        print("=" * 80)

        # =====================================================
        # PASO 4
        # =====================================================

        print("\n[4/5] Analizando contenido...")

        print("      🚧 CV Parser (próximamente)")

        # =====================================================
        # PASO 5
        # =====================================================

        print("\n[5/5] Construyendo Professional Profile...")

        print("      🚧 Professional Profile Builder (próximamente)")

        print("\n✅ Smart CV Engine finalizado correctamente.\n")

        return document


# =============================================================
# Prueba local
# =============================================================

if __name__ == "__main__":

    pipeline = SmartCVPipeline()

    document = pipeline.process(
        r"D:\PROYECTOS_FLUTTER\lia-employx\backend\tests\sample_files\CV_Miguel_Tovar_logistica_Spanish.pdf"
    )

    print("\nRESUMEN DEL DOCUMENTO\n")

    print(document.summary())