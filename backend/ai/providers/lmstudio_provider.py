"""
===============================================================
LIA EmployX

LM Studio Provider

Proveedor oficial para LM Studio.

Compatible con el AI Core.

Autor:
LIA EmployX Team
===============================================================
"""

from __future__ import annotations

import time
import requests

from backend.ai.config import (
    get_chat_url,
    get_models_url,
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    DEFAULT_MAX_TOKENS,
    DEFAULT_TIMEOUT,
)

from backend.ai.providers.base_provider import BaseProvider


class LMStudioProvider(BaseProvider):

    def __init__(self):

        super().__init__(
            provider_name="LM Studio",
            base_url=get_chat_url()
        )

        self.timeout = DEFAULT_TIMEOUT

        self.session = requests.Session()

    # ==========================================================
    # Conexión
    # ==========================================================

    def connect(self) -> bool:

        self.connected = self.health()

        return self.connected

    def disconnect(self):

        self.session.close()

        self.connected = False

    # ==========================================================
    # Estado
    # ==========================================================

    def health(self) -> bool:

        try:

            response = self.session.get(
                get_models_url(),
                timeout=5
            )

            self.connected = response.status_code == 200

            return self.connected

        except Exception:

            self.connected = False

            return False

    # ==========================================================
    # Modelos disponibles
    # ==========================================================

    def available_models(self):

        response = self.session.get(
            get_models_url(),
            timeout=5
        )

        response.raise_for_status()

        data = response.json()

        return [model["id"] for model in data["data"]]

    # ==========================================================
    # Chat
    # ==========================================================

    def chat(
        self,
        model=DEFAULT_MODEL,
        system_prompt="",
        user_prompt="",
        temperature=DEFAULT_TEMPERATURE,
        max_tokens=DEFAULT_MAX_TOKENS,
    ):

        payload = {

            "model": model,

            "temperature": temperature,

            "max_tokens": max_tokens,

            "messages": [

                {
                    "role": "system",
                    "content": system_prompt
                },

                {
                    "role": "user",
                    "content": user_prompt
                }

            ]

        }

        start = time.perf_counter()

        response = self.session.post(
            get_chat_url(),
            json=payload,
            timeout=self.timeout
        )

        elapsed = round(time.perf_counter() - start, 2)

        response.raise_for_status()

        data = response.json()

        answer = data["choices"][0]["message"]["content"]

        usage = data.get("usage", {})

        return {

            "success": True,

            "provider": "LM Studio",

            "model": model,

            "seconds": elapsed,

            "answer": answer,

            "prompt_tokens": usage.get("prompt_tokens", 0),

            "completion_tokens": usage.get("completion_tokens", 0),

            "total_tokens": usage.get("total_tokens", 0),

            "raw": data

        }

    # ==========================================================
    # Streaming
    # ==========================================================

    def stream(
        self,
        model,
        system_prompt,
        user_prompt,
        temperature,
        max_tokens
    ):

        payload = {

            "model": model,

            "stream": True,

            "temperature": temperature,

            "max_tokens": max_tokens,

            "messages": [

                {
                    "role": "system",
                    "content": system_prompt
                },

                {
                    "role": "user",
                    "content": user_prompt
                }

            ]

        }

        response = self.session.post(
            get_chat_url(),
            json=payload,
            stream=True,
            timeout=self.timeout
        )

        response.raise_for_status()

        for line in response.iter_lines():

            if line:

                yield line.decode("utf-8")

    # ==========================================================
    # Embeddings
    # ==========================================================

    def embeddings(self, model, text):

        raise NotImplementedError(
            "LM Studio aún no implementa embeddings en este provider."
        )

    # ==========================================================
    # Información
    # ==========================================================

    def info(self):

        return {

            "provider": "LM Studio",

            "connected": self.connected,

            "url": self.base_url,

            "timeout": self.timeout

        }

    # ==========================================================
    # Benchmark
    # ==========================================================

    def benchmark(self):

        result = self.chat(
            user_prompt="Responde únicamente OK."
        )

        return result["seconds"]