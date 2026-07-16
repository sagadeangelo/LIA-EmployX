"""
===============================================================
LIA EmployX

Prompt Builder

Construye los prompts enviados al modelo de IA.

Autor:
LIA EmployX Team
===============================================================
"""

from __future__ import annotations

import json

from backend.modules.cv.parser.schema_loader import SchemaLoader


class PromptBuilder:
    """
    Construye prompts para el Smart CV Parser.
    """

    def __init__(self):

        self.schema_loader = SchemaLoader()

    # ---------------------------------------------------------

    def build_cv_parser_prompt(
        self,
        document_text: str
    ) -> tuple[str, str]:
        """
        Devuelve:

            system_prompt,
            user_prompt
        """

        schema = self.schema_loader.load("cv_profile_schema")

        schema_json = json.dumps(
            schema,
            indent=2,
            ensure_ascii=False
        )

        system_prompt = f"""
Eres un especialista Senior en Recursos Humanos,
ATS (Applicant Tracking Systems)
y análisis profesional de currículums.

Tu misión es analizar el CV recibido y devolver
EXCLUSIVAMENTE un JSON válido.

NO inventes información.

Si un dato no existe escribe:

""

o

[]

según corresponda.

No agregues comentarios.

No agregues markdown.

No agregues explicación.

La respuesta debe cumplir EXACTAMENTE
el siguiente esquema JSON:

{schema_json}
"""

        user_prompt = f"""
Analiza el siguiente Currículum Vitae.

Extrae toda la información posible.

CV:

{document_text}
"""

        return system_prompt.strip(), user_prompt.strip()

    # ---------------------------------------------------------

    def build_summary_prompt(
        self,
        document_text: str
    ) -> tuple[str, str]:

        system_prompt = """
Eres un reclutador Senior.

Resume este CV en máximo 10 líneas.

No inventes información.
"""

        return system_prompt.strip(), document_text.strip()

    # ---------------------------------------------------------

    def build_improvement_prompt(
        self,
        document_text: str
    ) -> tuple[str, str]:

        system_prompt = """
Eres un experto internacional en redacción de CV.

Mejora el contenido.

No inventes experiencia.

No cambies fechas.

No cambies empresas.

Solo mejora redacción,
claridad,
impacto
y profesionalismo.
"""

        return system_prompt.strip(), document_text.strip()

    # ---------------------------------------------------------

    def build_translation_prompt(
        self,
        document_text: str,
        language: str
    ) -> tuple[str, str]:

        system_prompt = f"""
Traduce este currículum al idioma:

{language}

Mantén exactamente el mismo formato.

No inventes información.
"""

        return system_prompt.strip(), document_text.strip()


# ===============================================================
# Prueba local
# ===============================================================

if __name__ == "__main__":

    builder = PromptBuilder()

    system, user = builder.build_cv_parser_prompt(

        """
Miguel Tovar

Logistics Specialist

English B2

Google Data Analytics

7 years of experience
"""

    )

    print("=" * 70)

    print(system[:1500])

    print("=" * 70)

    print(user)