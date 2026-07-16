"""
===============================================================
LIA EmployX

Test CV Pipeline

Prueba completa del flujo:

PDF
    ↓
SmartCVEngine
    ↓
AICVParser
    ↓
ProfessionalProfile

Autor:
LIA EmployX Team
===============================================================
"""

from pathlib import Path

from backend.modules.cv.services.cv_analyzer import CVAnalyzer


def print_separator(title: str):

    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def main():

    print_separator("LIA EmployX - CV Pipeline Test")

    analyzer = CVAnalyzer()

    print("Estado del sistema:")

    health = analyzer.health()

    for key, value in health.items():
        print(f"  {key}: {'OK' if value else 'ERROR'}")

    print()

    file_path = input(
        "Ruta del CV (PDF/DOCX/TXT): "
    ).strip().strip('"')

    if not file_path:

        print("No se indicó ningún archivo.")

        return

    file_path = Path(file_path)

    if not file_path.exists():

        print("El archivo no existe.")

        return

    print()

    print("Analizando CV...")

    print()

    try:

        profile = analyzer.analyze(file_path)

    except Exception as ex:

        print_separator("ERROR")

        print(type(ex).__name__)

        print(ex)

        return

    print_separator("PROFESSIONAL PROFILE")

    try:

        print(
            "Nombre:",
            profile.personal_info.full_name
        )
    except:
        pass

    try:

        print(
            "Email:",
            profile.personal_info.email
        )
    except:
        pass

    try:

        print(
            "Teléfono:",
            profile.personal_info.phone
        )
    except:
        pass

    print()

    try:

        print(
            "Experiencias:",
            len(profile.experience)
        )
    except:
        pass

    try:

        print(
            "Educación:",
            len(profile.education)
        )
    except:
        pass

    try:

        print(
            "Skills:",
            len(profile.skills)
        )
    except:
        pass

    try:

        print(
            "Idiomas:",
            len(profile.languages)
        )
    except:
        pass

    try:

        print(
            "Certificaciones:",
            len(profile.certifications)
        )
    except:
        pass

    try:

        print(
            "Proyectos:",
            len(profile.projects)
        )
    except:
        pass

    print()

    print_separator("PIPELINE FINALIZADO")

    print("LIA EmployX procesó correctamente el CV.")


if __name__ == "__main__":

    main()