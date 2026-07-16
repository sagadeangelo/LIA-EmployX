"""
===============================================================
LIA EmployX
AI Core

config.py

Configuración centralizada del sistema de Inteligencia Artificial.

Toda la aplicación debe obtener su configuración desde aquí.

Autor:
LIA EmployX Team
===============================================================
"""

from __future__ import annotations

import os
from pathlib import Path

# ===============================================================
# Información del proyecto
# ===============================================================

PROJECT_NAME = "LIA EmployX"

AI_CORE_VERSION = "1.0.0"

DEBUG = True


# ===============================================================
# Directorios
# ===============================================================

ROOT_DIR = Path(__file__).resolve().parents[2]

BACKEND_DIR = ROOT_DIR / "backend"

AI_DIR = BACKEND_DIR / "ai"

PROMPTS_DIR = AI_DIR / "prompts"

MEMORY_DIR = AI_DIR / "memory"

EMBEDDINGS_DIR = AI_DIR / "embeddings"


# ===============================================================
# Provider por defecto
# ===============================================================

DEFAULT_PROVIDER = "lmstudio"


# ===============================================================
# LM Studio
# ===============================================================

LMSTUDIO_HOST = os.getenv("LMSTUDIO_HOST", "127.0.0.1")

LMSTUDIO_PORT = int(os.getenv("LMSTUDIO_PORT", "1234"))

LMSTUDIO_PROTOCOL = "http"

LMSTUDIO_BASE_URL = f"{LMSTUDIO_PROTOCOL}://" f"{LMSTUDIO_HOST}:" f"{LMSTUDIO_PORT}"

LMSTUDIO_API = LMSTUDIO_BASE_URL + "/v1"

LMSTUDIO_CHAT_ENDPOINT = LMSTUDIO_API + "/chat/completions"

LMSTUDIO_MODELS_ENDPOINT = LMSTUDIO_API + "/models"


# ===============================================================
# Modelo por defecto
# ===============================================================

DEFAULT_MODEL = "google/gemma-4-e4b"

# Puedes cambiarlo fácilmente a:

# DEFAULT_MODEL = "qwen3-8b"

# DEFAULT_MODEL = "llama-3.3"

# DEFAULT_MODEL = "deepseek-r1"


# ===============================================================
# Parámetros de inferencia
# ===============================================================

DEFAULT_TEMPERATURE = 0.20

DEFAULT_TOP_P = 0.95

DEFAULT_MAX_TOKENS = 4096

DEFAULT_TIMEOUT = 600

DEFAULT_STREAM = False


# ===============================================================
# Reintentos automáticos
# ===============================================================

MAX_RETRIES = 3

RETRY_DELAY_SECONDS = 2


# ===============================================================
# Logging
# ===============================================================

LOG_REQUESTS = True

LOG_RESPONSES = False

LOG_ERRORS = True

LOG_EXECUTION_TIME = True


# ===============================================================
# Cache
# ===============================================================

ENABLE_CACHE = True

CACHE_SIZE = 500

CACHE_EXPIRE_MINUTES = 60


# ===============================================================
# Embeddings
# ===============================================================

DEFAULT_EMBEDDING_MODEL = None

ENABLE_EMBEDDINGS = False


# ===============================================================
# Seguridad
# ===============================================================

VERIFY_SSL = False


# ===============================================================
# Utilidades
# ===============================================================


def get_chat_url() -> str:
    """
    Devuelve la URL del endpoint de chat.
    """
    return LMSTUDIO_CHAT_ENDPOINT


def get_models_url() -> str:
    """
    Devuelve la URL del endpoint de modelos.
    """
    return LMSTUDIO_MODELS_ENDPOINT


def get_provider() -> str:
    """
    Provider configurado.
    """
    return DEFAULT_PROVIDER


def get_default_model() -> str:
    """
    Modelo configurado.
    """
    return DEFAULT_MODEL


def print_configuration():

    print()

    print("=" * 70)

    print("LIA EmployX AI Core")

    print("=" * 70)

    print()

    print(f"Proyecto      : {PROJECT_NAME}")

    print(f"Versión       : {AI_CORE_VERSION}")

    print(f"Provider      : {DEFAULT_PROVIDER}")

    print(f"Modelo        : {DEFAULT_MODEL}")

    print(f"LM Studio     : {LMSTUDIO_BASE_URL}")

    print(f"Chat URL      : {LMSTUDIO_CHAT_ENDPOINT}")

    print(f"Models URL    : {LMSTUDIO_MODELS_ENDPOINT}")

    print()

    print("Parámetros")

    print("----------------------------")

    print(f"Temperature   : {DEFAULT_TEMPERATURE}")

    print(f"Top P         : {DEFAULT_TOP_P}")

    print(f"Max Tokens    : {DEFAULT_MAX_TOKENS}")

    print(f"Timeout       : {DEFAULT_TIMEOUT}")

    print()

    print("=" * 70)


if __name__ == "__main__":

    print_configuration()
