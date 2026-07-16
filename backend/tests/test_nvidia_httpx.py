"""
===============================================================
LIA EmployX

NVIDIA HTTPX TEST

Prueba usando HTTP/2 mediante httpx.

Autor:
LIA EmployX Team
===============================================================
"""

from __future__ import annotations

import json
import os
import time

import httpx
from dotenv import load_dotenv


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
    print("NVIDIA HTTPX TEST")
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
        "stream": False
    }

    print("URL:")
    print(url)
    print()

    print("HTTP/2:", True)
    print()

    print("=" * 70)
    print("PAYLOAD")
    print("=" * 70)

    print(
        json.dumps(
            payload,
            indent=4,
            ensure_ascii=False
        )
    )

    print()

    print("Enviando petición...")
    print()

    start = time.perf_counter()

    try:

        with httpx.Client(

            http2=True,

            timeout=httpx.Timeout(
                connect=15,
                read=60,
                write=15,
                pool=15
            )

        ) as client:

            response = client.post(

                url,

                headers=headers,

                json=payload

            )

        elapsed = time.perf_counter() - start

        print()
        print("=" * 70)
        print("RESPUESTA")
        print("=" * 70)

        print(f"HTTP Version : {response.http_version}")
        print(f"Status Code  : {response.status_code}")
        print(f"Tiempo       : {elapsed:.2f} s")

        print()
        print("Headers:")
        print("-" * 70)

        for k, v in response.headers.items():
            print(f"{k}: {v}")

        print()
        print("Body:")
        print("-" * 70)

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