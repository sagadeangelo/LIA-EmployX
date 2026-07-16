"""
===============================================================
LIA EmployX

Schema Loader

Carga automáticamente los esquemas JSON utilizados
por el Smart CV Parser.

Autor:
LIA EmployX Team
===============================================================
"""

from __future__ import annotations

import json
from pathlib import Path


class SchemaLoader:
    """
    Carga esquemas JSON desde backend/ai/schemas.
    """

    def __init__(self):

        self.schemas_path = (
            Path(__file__)
            .resolve()
            .parents[3]
            / "ai"
            / "schemas"
        )

    # ---------------------------------------------------------

    def load(self, schema_name: str) -> dict:
        """
        Carga un esquema JSON.

        Ejemplo:

            load("cv_profile_schema")
        """

        if not schema_name.endswith(".json"):
            schema_name += ".json"

        schema_file = self.schemas_path / schema_name

        if not schema_file.exists():
            raise FileNotFoundError(
                f"No existe el esquema:\n{schema_file}"
            )

        with open(schema_file, "r", encoding="utf-8") as f:
            return json.load(f)

    # ---------------------------------------------------------

    def exists(self, schema_name: str) -> bool:

        if not schema_name.endswith(".json"):
            schema_name += ".json"

        return (self.schemas_path / schema_name).exists()

    # ---------------------------------------------------------

    def available(self) -> list[str]:
        """
        Devuelve todos los esquemas disponibles.
        """

        return sorted(
            file.stem
            for file in self.schemas_path.glob("*.json")
        )

    # ---------------------------------------------------------

    def print_available(self):

        print()

        print("=" * 70)
        print("LIA EmployX Schemas")
        print("=" * 70)

        for schema in self.available():
            print(f"• {schema}")

        print()


# ==============================================================
# Prueba local
# ==============================================================

if __name__ == "__main__":

    loader = SchemaLoader()

    loader.print_available()

    schema = loader.load("cv_profile_schema")

    print(schema.keys())