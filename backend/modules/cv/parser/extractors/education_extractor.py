"""
===============================================================
LIA EmployX

Education Extractor

Extrae únicamente la formación académica.

Autor:
LIA EmployX Team
===============================================================
"""

from __future__ import annotations

from backend.ai.llm_manager import LLMManager
from backend.ai.models_catalog import AITask

from backend.modules.cv.parser.json_parser import JSONParser


class EducationExtractor:

    def __init__(self):

        self.llm = LLMManager()

        self.parser = JSONParser()

    # ---------------------------------------------------------

    def extract(self, cv_text: str) -> list:

        system_prompt = """
Eres un especialista en Recursos Humanos.

Extrae ÚNICAMENTE la formación académica.

Devuelve exclusivamente un JSON válido.

Formato EXACTO:

[
    {
        "institution": "",
        "degree": "",
        "field_of_study": "",
        "start_date": "",
        "end_date": "",
        "current": false,
        "description": "",
        "location": "",
        "grade": ""
    }
]

Reglas:

- No inventes información.
- Si un dato no existe usa "".
- Si el candidato aún estudia usa current=true.
- Devuelve únicamente JSON.
- No escribas explicaciones.
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