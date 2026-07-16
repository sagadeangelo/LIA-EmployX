"""
===============================================================
LIA EmployX

Languages Extractor

Extrae únicamente los idiomas del candidato.

Autor:
LIA EmployX Team
===============================================================
"""

from __future__ import annotations

from backend.ai.llm_manager import LLMManager
from backend.ai.models_catalog import AITask

from backend.modules.cv.parser.json_parser import JSONParser


class LanguagesExtractor:

    def __init__(self):

        self.llm = LLMManager()

        self.parser = JSONParser()

    # ---------------------------------------------------------

    def extract(self, cv_text: str) -> list:

        system_prompt = """
Eres un especialista en Recursos Humanos.

Extrae ÚNICAMENTE los idiomas mencionados en el CV.

Devuelve únicamente JSON válido.

Formato EXACTO:

[
    {
        "language": "",
        "level": "",
        "certification": ""
    }
]

Ejemplos de nivel:

Native
A1
A2
B1
B2
C1
C2
Basic
Intermediate
Advanced
Professional

Reglas:

- No inventes idiomas.
- Si no se menciona el nivel usa "".
- Si no existe certificación usa "".
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