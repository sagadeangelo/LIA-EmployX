"""
===============================================================
LIA EmployX

NVIDIA REST API TEST

Diagnóstico completo usando requests.

Autor:
LIA EmployX Team
===============================================================
"""

from __future__ import annotations

import http.client as http_client
import json
import logging
import os
import time

import requests
from dotenv import load_dotenv

# ===============================================================
# HTTP DEBUG
# ===============================================================

http_client.HTTPConnection.debuglevel = 1

logging.basicConfig(level=logging.DEBUG)

logging.getLogger("urllib3").setLevel(logging.DEBUG)

logging.getLogger("urllib3").propagate = True

# ===============================================================
# Variables de entorno
# ===============================================================

load_dotenv()

API_KEY = os.getenv("NVIDIA_API_KEY")

BASE_URL = os.getenv(
    "NVIDIA_BASE_URL",
    "https://integrate.api.nvidia.com/v1",
)

MODEL = os.getenv(
    "NVIDIA_MODEL",
    "meta/llama-3.3-70b-instruct",
)

# ===============================================================


def main():

    print()
    print("=" * 70)
    print("LIA EmployX")
    print("NVIDIA REST TEST")
    print("=" * 70)
    print()

    if not API_KEY:
        raise RuntimeError("No existe NVIDIA_API_KEY")

    url = f"{BASE_URL}/chat/completions"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": "Reply ONLY with OK."
            }
        ],
        "temperature": 0,
        "top_p": 1,
        "max_tokens": 5,
        "stream": False,
    }

    print("URL")
    print(url)
    print()

    print("=" * 70)
    print("HEADERS")
    print("=" * 70)

    print(
        json.dumps(
            {
                k: (
                    "***API KEY***"
                    if k == "Authorization"
                    else v
                )
                for k, v in headers.items()
            },
            indent=4,
        )
    )

    print()

    print("=" * 70)
    print("PAYLOAD")
    print("=" * 70)

    print(
        json.dumps(
            payload,
            indent=4,
            ensure_ascii=False,
        )
    )

    print()

    print("Enviando petición...")
    print()

    session = requests.Session()

    start = time.perf_counter()

    try:

        response = session.post(
            url=url,
            headers=headers,
            json=payload,
            timeout=(15, 60),
        )

        elapsed = time.perf_counter() - start

        print()
        print("=" * 70)
        print("RESPUESTA")
        print("=" * 70)

        print(f"Status : {response.status_code}")
        print(f"Tiempo : {elapsed:.2f} s")
        print()

        print(response.text)

    except Exception as ex:

        elapsed = time.perf_counter() - start

        print()
        print("=" * 70)
        print("EXCEPCIÓN")
        print("=" * 70)

        print(type(ex).__name__)
        print()

        print(ex)

        print()

        print(f"Tiempo hasta error: {elapsed:.2f} s")


# ===============================================================

if __name__ == "__main__":
    main()