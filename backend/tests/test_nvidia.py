"""
===============================================================
LIA EmployX

NVIDIA API Test

Prueba independiente de conexión con NVIDIA NIM API.

Autor:
LIA EmployX Team
===============================================================
"""

from __future__ import annotations

import os
import time
import traceback

from dotenv import load_dotenv
from openai import OpenAI


# ===============================================================
# Variables de entorno
# ===============================================================

load_dotenv()

API_KEY = os.getenv("NVIDIA_API_KEY")

BASE_URL = os.getenv(
    "NVIDIA_BASE_URL",
    "https://integrate.api.nvidia.com/v1"
)

MODEL = os.getenv(
    "NVIDIA_MODEL",
    "meta/llama-3.3-70b-instruct"
)


# ===============================================================

def main():

    print()
    print("=" * 70)
    print("LIA EmployX")
    print("NVIDIA API TEST")
    print("=" * 70)
    print()

    if not API_KEY:
        raise RuntimeError(
            "No existe NVIDIA_API_KEY en el archivo .env"
        )

    print(f"Modelo   : {MODEL}")
    print(f"Endpoint : {BASE_URL}")
    print()

    print("Creando cliente...")

    client = OpenAI(

        base_url=BASE_URL,

        api_key=API_KEY,

        timeout=30.0

    )

    print("Cliente creado.")
    print()

    print("Enviando solicitud a NVIDIA...")
    print()

    start = time.perf_counter()

    try:

        response = client.chat.completions.create(

            model=MODEL,

            temperature=0,

            max_tokens=5,

            messages=[
                {
                    "role": "user",
                    "content": "Reply ONLY with OK."
                }
            ]

        )

    except Exception as e:

        print()
        print("=" * 70)
        print("ERROR")
        print("=" * 70)

        print(type(e).__name__)
        print()
        print(e)
        print()

        traceback.print_exc()

        return

    elapsed = time.perf_counter() - start

    print()
    print("Respuesta recibida.")
    print()

    answer = response.choices[0].message.content.strip()

    print("=" * 70)
    print("RESPUESTA")
    print("=" * 70)
    print()

    print(answer)

    print()

    print("=" * 70)
    print("ESTADÍSTICAS")
    print("=" * 70)

    print(f"Tiempo : {elapsed:.2f} s")

    if getattr(response, "usage", None):

        print(f"Prompt Tokens     : {response.usage.prompt_tokens}")
        print(f"Completion Tokens : {response.usage.completion_tokens}")
        print(f"Total Tokens      : {response.usage.total_tokens}")

    print()


# ===============================================================

if __name__ == "__main__":
    main()