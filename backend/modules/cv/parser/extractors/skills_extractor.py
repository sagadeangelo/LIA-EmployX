"""
===============================================================
LIA EmployX

Skills Extractor

Extrae únicamente las habilidades del candidato.

Autor:
LIA EmployX Team
===============================================================
"""

from __future__ import annotations

from backend.ai.llm_manager import LLMManager
from backend.ai.models_catalog import AITask

from backend.modules.cv.parser.json_parser import JSONParser


class SkillsExtractor:

    def __init__(self):

        self.llm = LLMManager()

        self.parser = JSONParser()

    # ---------------------------------------------------------

    def extract(self, cv_text: str) -> list:

        system_prompt = """
Eres un especialista en Recursos Humanos.

Extrae ÚNICAMENTE las habilidades del candidato.

Incluye:

- Habilidades técnicas
- Soft Skills
- Herramientas
- Frameworks
- Lenguajes de programación
- Bases de datos
- Plataformas
- Tecnologías

Devuelve exclusivamente un JSON válido.

Formato EXACTO:

[
    {
        "name": "",
        "category": "",
        "level": ""
    }
]

Categorías sugeridas:

Technical
Programming
Database
Cloud
Framework
Tool
Soft Skill
Language
Office
Other

Reglas:

- No inventes habilidades.
- No agregues texto fuera del JSON.
- Si no conoces el nivel usa "".
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