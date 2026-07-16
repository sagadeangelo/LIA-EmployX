"""
===============================================================
LIA EmployX

CV Validator

Valida y normaliza el JSON devuelto por la IA.

Autor:
LIA EmployX Team
===========================================================================
"""

from __future__ import annotations

from copy import deepcopy

from backend.modules.cv.parser.schema_loader import SchemaLoader


class CVValidator:
    """
    Valida la estructura del JSON generado por la IA.

    También completa automáticamente campos faltantes.
    """

    def __init__(self):

        loader = SchemaLoader()

        self.schema = loader.load("cv_profile_schema")

    # ==========================================================
    # API pública
    # ==========================================================

    def validate(self, data: dict) -> dict:
        """
        Devuelve un JSON válido según el esquema.
        """

        if not isinstance(data, dict):
            raise TypeError(
                "La IA no devolvió un objeto JSON."
            )

        return self._merge(
            deepcopy(self.schema),
            data
        )

    # ==========================================================
    # Merge recursivo
    # ==========================================================

    def _merge(
        self,
        schema,
        data
    ):

        # -------------------------------
        # Diccionarios
        # -------------------------------

        if isinstance(schema, dict):

            result = {}

            for key, value in schema.items():

                if key in data:

                    result[key] = self._merge(
                        value,
                        data[key]
                    )

                else:

                    result[key] = deepcopy(value)

            return result

        # -------------------------------
        # Listas
        # -------------------------------

        if isinstance(schema, list):

            if not isinstance(data, list):

                return deepcopy(schema)

            if len(schema) == 0:

                return data

            template = schema[0]

            return [

                self._merge(
                    template,
                    item
                )

                for item in data

            ]

        # -------------------------------
        # Valores simples
        # -------------------------------

        return data

    # ==========================================================
    # Utilidades
    # ==========================================================

    def has_required_sections(
        self,
        data: dict
    ) -> bool:

        required = [

            "personal_info",

            "experience",

            "education",

            "skills",

            "languages"

        ]

        return all(

            key in data

            for key in required

        )

    # ==========================================================

    def print_summary(
        self,
        data: dict
    ):

        print()

        print("=" * 70)

        print("CV Validator")

        print("=" * 70)

        print()

        for key in sorted(data.keys()):

            value = data[key]

            if isinstance(value, list):

                print(f"{key:<20} {len(value)} elementos")

            elif isinstance(value, dict):

                print(f"{key:<20} objeto")

            else:

                print(f"{key:<20} {value}")

        print()


# ==============================================================
# Prueba local
# ==============================================================

if __name__ == "__main__":

    validator = CVValidator()

    ejemplo = {

        "personal_info": {

            "full_name": "Miguel Tovar"

        },

        "skills": [

            {

                "name": "Flutter"

            }

        ]

    }

    resultado = validator.validate(ejemplo)

    validator.print_summary(resultado)