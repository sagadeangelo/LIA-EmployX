"""
===============================================================
LIA EmployX

AI CV Parser

Servicio encargado de convertir el texto de un CV
en un ProfessionalProfile utilizando IA.

Pipeline:

DocumentContent
        ↓
PromptBuilder
        ↓
LLMManager
        ↓
Gemma
        ↓
JSONParser
        ↓
Validator
        ↓
ProfileMapper
        ↓
ProfessionalProfile

Autor:
LIA EmployX Team
===============================================================
"""

from __future__ import annotations

import time

from backend.ai.llm_manager import LLMManager
from backend.ai.models_catalog import AITask

from backend.modules.cv.parser.prompt_builder import PromptBuilder
from backend.modules.cv.parser.json_parser import JSONParser
from backend.modules.cv.parser.validator import CVValidator
from backend.modules.cv.parser.profile_mapper import ProfileMapper


class AICVParser:
    """
    Servicio principal de análisis de CV mediante IA.
    """

    def __init__(self):

        self.llm = LLMManager()

        self.prompt_builder = PromptBuilder()

        self.json_parser = JSONParser()

        self.validator = CVValidator()

        self.mapper = ProfileMapper()

    # ---------------------------------------------------------

    def parse(self, document_text: str):

        """
        Convierte un CV en texto a ProfessionalProfile.
        """

        if not document_text:

            raise ValueError("El documento está vacío.")

        print()

        print("=" * 70)
        print("LIA EmployX")
        print("AI CV Parser")
        print("=" * 70)

        start = time.time()

        # -----------------------------------------------------
        # Construcción del prompt
        # -----------------------------------------------------

        system_prompt, user_prompt = (

            self.prompt_builder.build_cv_parser_prompt(

                document_text

            )

        )

        # -----------------------------------------------------
        # IA
        # -----------------------------------------------------

        response = self.llm.ask(

            task=AITask.CV_PARSER,

            prompt=user_prompt,

            system_prompt=system_prompt

        )

        # -----------------------------------------------------
        # Algunas implementaciones del provider regresan
        # un string y otras un diccionario.
        # -----------------------------------------------------

        if isinstance(response, dict):

            answer = response.get("answer", "")

        else:

            answer = response

        # -----------------------------------------------------
        # JSON
        # -----------------------------------------------------

        data = self.json_parser.parse(answer)

        # -----------------------------------------------------
        # Validación
        # -----------------------------------------------------

        data = self.validator.validate(data)

        # -----------------------------------------------------
        # Mapping
        # -----------------------------------------------------

        profile = self.mapper.map(data)

        elapsed = round(time.time() - start, 2)

        print()

        print("=" * 70)

        print(f"CV procesado correctamente ({elapsed} s)")

        print("=" * 70)

        return profile

    # ---------------------------------------------------------

    def parse_to_json(self, document_text: str):

        """
        Devuelve únicamente el JSON validado.
        """

        system_prompt, user_prompt = (

            self.prompt_builder.build_cv_parser_prompt(

                document_text

            )

        )

        response = self.llm.ask(

            task=AITask.CV_PARSER,

            prompt=user_prompt,

            system_prompt=system_prompt

        )

        if isinstance(response, dict):

            answer = response.get("answer", "")

        else:

            answer = response

        data = self.json_parser.parse(answer)

        return self.validator.validate(data)

    # ---------------------------------------------------------

    def is_ready(self):

        """
        Verifica si el sistema de IA está disponible.
        """

        return self.llm.is_online()