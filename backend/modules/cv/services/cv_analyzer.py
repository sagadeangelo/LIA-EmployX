"""
===============================================================
LIA EmployX

CV Analyzer

Orquestador principal del análisis de Currículums.

Pipeline:

Archivo
    ↓
SmartCVEngine
    ↓
DocumentContent
    ↓
ParserOrchestrator
    ↓
ProfessionalProfile

Autor:
LIA EmployX Team
===============================================================
"""

from __future__ import annotations

from pathlib import Path

from backend.modules.cv.engine.smart_cv_engine import SmartCVEngine
from backend.modules.cv.parser.parser_orchestrator import ParserOrchestrator


class CVAnalyzer:
    """
    Analizador completo de Currículums.
    """

    def __init__(self):

        self.engine = SmartCVEngine()

        self.parser = ParserOrchestrator()

    # ---------------------------------------------------------

    def analyze(self, file_path: str):

        file_path = Path(file_path)

        if not file_path.exists():

            raise FileNotFoundError(file_path)

        print()

        print("=" * 70)
        print("LIA EmployX")
        print("CV Analyzer")
        print("=" * 70)

        # -----------------------------------------------------
        # Leer documento
        # -----------------------------------------------------

        document = self.engine.read(file_path)

        if not document.text.strip():

            raise ValueError(
                "No fue posible extraer texto del documento."
            )

        print()

        print("Texto extraído:")

        print(f"{len(document.text):,} caracteres")

        # -----------------------------------------------------
        # Parser Orchestrator
        # -----------------------------------------------------

        profile = self.parser.parse(

            document.text

        )

        return profile

    # ---------------------------------------------------------

    def analyze_text(self, text: str):

        return self.parser.parse(text)

    # ---------------------------------------------------------

    def health(self):

        return {

            "engine": True,

            "parser": True

        }


# ===========================================================
# Prueba local
# ===========================================================

if __name__ == "__main__":

    analyzer = CVAnalyzer()

    print()

    print(analyzer.health())