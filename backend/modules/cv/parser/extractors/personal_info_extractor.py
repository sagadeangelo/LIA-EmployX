"""
===============================================================
LIA EmployX

Personal Info Extractor

Extrae únicamente la información personal del CV.

Autor:
LIA EmployX Team
===============================================================
"""

from __future__ import annotations

from backend.ai.llm_manager import LLMManager
from backend.ai.models_catalog import AITask

from backend.modules.cv.parser.json_parser import JSONParser


class PersonalInfoExtractor:

    def __init__(self):

        self.llm = LLMManager()

        self.parser = JSONParser()

    # ---------------------------------------------------------

    def extract(self, cv_text: str) -> dict:

        system_prompt = """
Eres un especialista en Recursos Humanos.

Extrae ÚNICAMENTE la información personal.

Devuelve únicamente JSON válido.

Formato EXACTO:

{
  "full_name": "",
  "email": "",
  "phone": "",
  "city": "",
  "country": "",
  "linkedin": "",
  "github": "",
  "portfolio": "",
  "summary": ""
}

No agregues texto antes ni después del JSON.
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