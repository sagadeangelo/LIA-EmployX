"""
===============================================================
LIA EmployX

CV Specialist

Especialista encargado de analizar el CV del usuario.
===============================================================
"""

from pathlib import Path

from backend.agents.base.base_agent import BaseAgent
from backend.modules.cv.engine.pipeline import SmartCVPipeline


class CVAgent(BaseAgent):
    """
    Especialista encargado del análisis de Currículums.

    Responsabilidades:

        • Leer CV
        • Analizar CV
        • Construir Professional Profile
        • Guardarlo en el Context
        • Emitir eventos
    """

    def __init__(self):

        super().__init__(
            name="CV Specialist",
            description="Analiza el CV del usuario y construye el perfil profesional.",
            version="1.0.0"
        )

        self.pipeline = SmartCVPipeline()

    # ---------------------------------------------------------

    def run(self, file_path: str):

        self.status = "running"

        self.log("=" * 60)
        self.log("Iniciando análisis del CV...")
        self.log("=" * 60)

        if not Path(file_path).exists():
            raise FileNotFoundError(file_path)

        # -----------------------------------------------------
        # Ejecutar Smart CV Engine
        # -----------------------------------------------------

        document = self.pipeline.process(file_path)

        # -----------------------------------------------------
        # Guardar resultado en el contexto
        # -----------------------------------------------------

        if self.context is not None:

            self.context.set(
                "document",
                document
            )

            self.context.add_event(
                "CV analizado correctamente."
            )

        # -----------------------------------------------------
        # Emitir evento
        # -----------------------------------------------------

        self.emit_event("CV_ANALYZED")

        self.status = "finished"

        self.log("Análisis completado.")

        return document

    # ---------------------------------------------------------

    def validate(self):

        self.log("Validando CV...")

        return True

    # ---------------------------------------------------------

    def summary(self):

        return {

            "name": self.name,
            "description": self.description,
            "version": self.version,
            "status": self.status,

        }