"""
===============================================================
LIA EmployX

LLM Manager

Orquestador central de todos los modelos de IA.

Ningún agente debe comunicarse directamente con un Provider.

Autor:
LIA EmployX Team
===============================================================
"""

from __future__ import annotations

from backend.ai.models_catalog import (
    AITask,
    get_model,
)

from backend.ai.providers.lmstudio_provider import LMStudioProvider


class LLMManager:

    """
    Cerebro del AI Core.

    Se encarga de:

    • Elegir el modelo adecuado

    • Elegir el provider

    • Ejecutar prompts

    • Devolver respuestas estandarizadas
    """

    def __init__(self):

        self.provider = LMStudioProvider()

        self.provider.connect()

    # ---------------------------------------------------------

    def is_online(self):

        return self.provider.health()

    # ---------------------------------------------------------

    def models(self):

        return self.provider.available_models()

    # ---------------------------------------------------------

    def ask(

        self,

        task: AITask,

        prompt: str,

        system_prompt: str = ""

    ):

        model = get_model(task)

        print()

        print("=" * 70)

        print("LIA EmployX AI")

        print("=" * 70)

        print()

        print(f"Tarea      : {task.value}")

        print(f"Modelo     : {model.name}")

        print(f"Provider   : {model.provider}")

        print()

        result = self.provider.chat(

            model=model.name,

            system_prompt=system_prompt,

            user_prompt=prompt,

            temperature=model.temperature,

            max_tokens=model.max_tokens

        )

        return result

    # ---------------------------------------------------------

    def cv_parser(

        self,

        text: str

    ):

        return self.ask(

            task=AITask.CV_PARSER,

            prompt=text,

            system_prompt="""
Eres un especialista en Recursos Humanos.

Extrae toda la información del CV.

Devuelve únicamente JSON.
"""

        )

    # ---------------------------------------------------------

    def ats_score(

        self,

        cv,

        vacancy

    ):

        prompt = f"""

CV

{cv}


VACANTE

{vacancy}

"""

        return self.ask(

            task=AITask.ATS_SCORE,

            prompt=prompt,

            system_prompt="""
Calcula el ATS Score.

Devuelve únicamente JSON.
"""

        )

    # ---------------------------------------------------------

    def translate(

        self,

        text,

        language

    ):

        return self.ask(

            task=AITask.TRANSLATION,

            prompt=text,

            system_prompt=f"""
Traduce al idioma {language}.

Conserva el formato.
"""

        )

    # ---------------------------------------------------------

    def interview(

        self,

        profile,

        vacancy

    ):

        prompt = f"""

Perfil

{profile}

Vacante

{vacancy}

"""

        return self.ask(

            task=AITask.INTERVIEW,

            prompt=prompt,

            system_prompt="""
Eres un entrevistador Senior.

Genera preguntas para el candidato.
"""

        )

    # ---------------------------------------------------------

    def summary(

        self,

        text

    ):

        return self.ask(

            task=AITask.CV_SUMMARY,

            prompt=text,

            system_prompt="""
Resume el siguiente texto profesionalmente.
"""

        )

    # ---------------------------------------------------------

    def improve_resume(

        self,

        text

    ):

        return self.ask(

            task=AITask.CV_IMPROVEMENT,

            prompt=text,

            system_prompt="""
Mejora este CV profesionalmente.

No inventes información.

Solo mejora redacción.
"""

        )

    # ---------------------------------------------------------

    def provider_info(self):

        return self.provider.info()