"""
===============================================================
LIA EmployX

AI Models Catalog

Catálogo central de tareas y modelos.

El resto del sistema NUNCA debe conocer nombres de modelos.

Siempre preguntará por una tarea.

Autor:
LIA EmployX Team
===============================================================
"""

from __future__ import annotations

from enum import Enum
from dataclasses import dataclass

from backend.ai.config import DEFAULT_MODEL


# ===============================================================
# Tipos de tareas
# ===============================================================

class AITask(str, Enum):

    # CV
    CV_PARSER = "cv_parser"
    CV_SUMMARY = "cv_summary"
    CV_IMPROVEMENT = "cv_improvement"
    CV_TRANSLATION = "cv_translation"

    # ATS
    ATS_SCORE = "ats_score"
    ATS_OPTIMIZATION = "ats_optimization"

    # Vacantes
    JOB_MATCHING = "job_matching"
    JOB_ANALYSIS = "job_analysis"

    # Entrevistas
    INTERVIEW = "interview"

    # Aprendizaje
    LEARNING = "learning"

    # Certificaciones
    CERTIFICATIONS = "certifications"

    # Libros
    BOOKS = "books"

    # Networking
    NETWORKING = "networking"

    # Traducción
    TRANSLATION = "translation"

    # Chat
    CHAT = "chat"


# ===============================================================
# Modelo
# ===============================================================

@dataclass(slots=True)
class AIModel:

    name: str

    provider: str

    temperature: float = 0.20

    max_tokens: int = 4096

    description: str = ""


# ===============================================================
# Catálogo
# ===============================================================

MODELS = {

    "default": AIModel(

        name=DEFAULT_MODEL,

        provider="lmstudio",

        description="Modelo por defecto"

    ),

    "gemma": AIModel(

        name=DEFAULT_MODEL,

        provider="lmstudio",

        temperature=0.20,

        max_tokens=4096,

        description="Especialista en análisis de CV"

    ),

    "qwen": AIModel(

        name="qwen",

        provider="lmstudio",

        temperature=0.20,

        max_tokens=4096,

        description="Especialista ATS"

    ),

    "embedding": AIModel(

        name="text-embedding-nomic-embed-text-v1.5",

        provider="lmstudio",

        description="Embeddings"

    )

}


# ===============================================================
# Relación tarea → modelo
# ===============================================================

TASK_MODEL = {

    AITask.CV_PARSER: "gemma",

    AITask.CV_SUMMARY: "gemma",

    AITask.CV_IMPROVEMENT: "gemma",

    AITask.CV_TRANSLATION: "gemma",

    AITask.ATS_SCORE: "qwen",

    AITask.ATS_OPTIMIZATION: "qwen",

    AITask.JOB_MATCHING: "qwen",

    AITask.JOB_ANALYSIS: "qwen",

    AITask.INTERVIEW: "qwen",

    AITask.LEARNING: "gemma",

    AITask.CERTIFICATIONS: "gemma",

    AITask.BOOKS: "gemma",

    AITask.NETWORKING: "qwen",

    AITask.TRANSLATION: "gemma",

    AITask.CHAT: "default"

}


# ===============================================================
# Funciones
# ===============================================================

def get_model(task: AITask) -> AIModel:

    key = TASK_MODEL.get(task, "default")

    return MODELS[key]


def get_model_name(task: AITask) -> str:

    return get_model(task).name


def get_provider(task: AITask) -> str:

    return get_model(task).provider


def print_catalog():

    print()

    print("=" * 70)

    print("LIA EmployX AI Models")

    print("=" * 70)

    print()

    for task in AITask:

        model = get_model(task)

        print(

            f"{task.value:<25}"

            f"{model.name}"

        )

    print()

    print("=" * 70)


if __name__ == "__main__":

    print_catalog()