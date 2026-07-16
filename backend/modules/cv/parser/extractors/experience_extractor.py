"""
===============================================================
LIA EmployX

Experience Extractor

Extrae únicamente la experiencia laboral.

Autor:
LIA EmployX Team
===============================================================
"""

from __future__ import annotations

from backend.ai.llm_manager import LLMManager
from backend.ai.models_catalog import AITask

from backend.modules.cv.parser.json_parser import JSONParser


class ExperienceExtractor:

    def __init__(self):

        self.llm = LLMManager()

        self.parser = JSONParser()

    # ---------------------------------------------------------

    def extract(self, cv_text: str) -> list:

        system_prompt = """
Eres un especialista en Recursos Humanos.

Extrae ÚNICAMENTE la experiencia laboral.

Devuelve únicamente un JSON válido.

Formato EXACTO:

[
    {
        "company": "",
        "position": "",
        "location": "",
        "employment_type": "",
        "start_date": "",
        "end_date": "",
        "current": false,
        "description": "",
        "achievements": []
    }
]

Reglas:

- No inventes información.
- Si un dato no existe usa "".
- Si continúa trabajando usa current=true.
- achievements debe ser un arreglo.
- No escribas texto antes ni después del JSON.
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