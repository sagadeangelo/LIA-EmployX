"""
===============================================================================
LIA EmployX

Test: CVSectionSplitter

Permite validar el funcionamiento del nuevo CVSectionSplitter
sin utilizar IA.

Autor:
LIA EmployX Team
===============================================================================
"""

from pathlib import Path
import sys


# =============================================================================
# Configuración
# =============================================================================

CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# =============================================================================
# Imports
# =============================================================================

from backend.modules.cv.engine.smart_cv_engine import SmartCVEngine
from backend.modules.cv.parser.cv_section_splitter import CVSectionSplitter


# =============================================================================
# Utilidades
# =============================================================================

def separator():

    print("=" * 70)


# =============================================================================
# Main
# =============================================================================

def main():

    separator()
    print("LIA EmployX - CVSectionSplitter Test")
    separator()

    print()

    path = input("Ruta del CV: ").strip().strip('"')

    if not path:

        print("No se proporcionó ruta.")

        return

    path = Path(path)

    if not path.exists():

        print()

        print("Archivo no encontrado:")

        print(path)

        return

    print()

    print("Leyendo documento...")

    print()

    engine = SmartCVEngine()

    document = engine.read(path)

    print()

    print("Texto extraído:")

    print(f"{len(document.text):,} caracteres")

    splitter = CVSectionSplitter()

    print()

    separator()

    print("Procesando splitter")

    separator()

    print()

    # ==============================================
    # Procesar
    # ==============================================

    sections = splitter.process(

        document.text

    )

    # ==============================================
    # Resumen
    # ==============================================

    print()

    separator()

    print("RESUMEN")

    separator()

    print()

    for name, content in sections.items():

        print(

            f"{name:20}"

            f"{len(content):6}"

            f" caracteres"

        )

    # ==============================================
    # Contenido
    # ==============================================

    print()

    separator()

    print("CONTENIDO")

    separator()

    print()

    for name, content in sections.items():

        print()

        print("-" * 70)

        print(name.upper())

        print("-" * 70)

        print()

        if content:

            print(content)

        else:

            print("(Vacío)")

    print()

    separator()

    print("FIN DEL TEST")

    separator()


# =============================================================================

if __name__ == "__main__":

    main()