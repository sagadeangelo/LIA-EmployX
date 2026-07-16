"""
===============================================================
LIA EmployX

Projects Extractor

Extrae únicamente los proyectos profesionales
o personales relevantes del candidato.

Autor:
LIA EmployX Team
===============================================================
"""

from __future__ import annotations

from backend.ai.llm_manager import LLMManager
from backend.ai.models_catalog import AITask

from backend.modules.cv.parser.json_parser import JSONParser


class ProjectsExtractor:

    def __init__(self):

        self.llm = LLMManager()

        self.parser = JSONParser()

    # ---------------------------------------------------------

    def extract(self, cv_text: str) -> list:

        system_prompt = """
Eres un especialista en Recursos Humanos.

Extrae ÚNICAMENTE los proyectos relevantes del CV.

Incluye:

- Proyectos profesionales
- Proyectos personales
- Open Source
- Freelance
- Investigación
- Portafolio

Devuelve exclusivamente un JSON válido.

Formato EXACTO:

[
    {
        "name": "",
        "role": "",
        "description": "",
        "technologies": [],
        "url": "",
        "start_date": "",
        "end_date": ""
    }
]

Reglas:

- No inventes proyectos.
- technologies debe ser un arreglo.
- Si no existe información usa "".
- No agregues texto fuera del JSON.
"""

        response = self.llm.ask(

            task=AITask.CV_PARSER,

            prompt=cv_text,

            system_prompt=system_prompt

        )

        if isinstance(response, dict):

            answer = response.get("answer", "")

        else:

            answer = response

        return self.parser.parse(answer)