"""
===============================================================
LIA EmployX

Certifications Extractor

Extrae únicamente las certificaciones del candidato.

Autor:
LIA EmployX Team
===============================================================
"""

from __future__ import annotations

from backend.ai.llm_manager import LLMManager
from backend.ai.models_catalog import AITask

from backend.modules.cv.parser.json_parser import JSONParser


class CertificationsExtractor:

    def __init__(self):

        self.llm = LLMManager()

        self.parser = JSONParser()

    # ---------------------------------------------------------

    def extract(self, cv_text: str) -> list:

        system_prompt = """
Eres un especialista en Recursos Humanos.

Extrae ÚNICAMENTE las certificaciones obtenidas por el candidato.

Devuelve exclusivamente un JSON válido.

Formato EXACTO:

[
    {
        "name": "",
        "issuer": "",
        "issue_date": "",
        "expiration_date": "",
        "credential_id": "",
        "credential_url": ""
    }
]

Reglas:

- No inventes certificaciones.
- Si un dato no existe usa "".
- Devuelve únicamente JSON.
- No agregues comentarios ni explicaciones.
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