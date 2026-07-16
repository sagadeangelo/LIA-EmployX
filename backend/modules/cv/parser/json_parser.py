"""
LIA EmployX - JSON Parser
"""

from __future__ import annotations

import json
import re


class JSONParser:

    def parse(self, response: str) -> dict:

        if not response:
            raise ValueError("La respuesta está vacía.")

        cleaned = self.clean(response)

        try:
            return json.loads(cleaned)

        except json.JSONDecodeError as e:
            raise ValueError(f"No fue posible interpretar el JSON.\n{e}")

    def clean(self, text: str) -> str:

        text = text.strip()

        text = re.sub(r"```json", "", text, flags=re.IGNORECASE)
        text = re.sub(r"```", "", text)

        start = text.find("{")

        if start != -1:
            text = text[start:]

        end = text.rfind("}")

        if end != -1:
            text = text[: end + 1]

        return text.strip()

    def is_json(self, text: str) -> bool:

        try:
            json.loads(self.clean(text))
            return True
        except Exception:
            return False

    def pretty(self, data: dict) -> str:

        return json.dumps(
            data,
            indent=4,
            ensure_ascii=False
        )