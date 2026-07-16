"""
===============================================================
LIA EmployX

Test Smart CV Engine

Prueba el motor de lectura de documentos.

Autor:
LIA EmployX Team
===============================================================
"""

from pathlib import Path

from backend.modules.cv.engine.smart_cv_engine import SmartCVEngine


def main():

    print("=" * 70)
    print("LIA EmployX - Smart CV Engine Test")
    print("=" * 70)
    print()

    engine = SmartCVEngine()

    print("Formatos soportados:")

    for ext in engine.supported_extensions():
        print(f"   ✓ {ext}")

    print()

    file = input("Ruta del archivo (PDF/DOCX/Imagen): ").strip().strip('"')

    if not file:

        print("No se seleccionó ningún archivo.")

        return

    file = Path(file)

    if not file.exists():

        print()

        print("ERROR")

        print("El archivo no existe.")

        return

    print()

    print("Leyendo documento...")

    print()

    document = engine.read(file)

    print("=" * 70)

    print("RESUMEN")

    print("=" * 70)

    summary = document.summary()

    for key, value in summary.items():

        print(f"{key:15}: {value}")

    print()

    print("=" * 70)
    print("PRIMEROS 1500 CARACTERES")
    print("=" * 70)
    print()

    print(document.text[:1500])

    print()

    print("=" * 70)

    print(f"Total caracteres : {document.characters:,}")

    print(f"Total palabras   : {document.words:,}")

    print(f"Total líneas     : {document.lines:,}")

    print("=" * 70)


if __name__ == "__main__":

    main()