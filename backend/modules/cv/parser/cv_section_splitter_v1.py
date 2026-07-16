"""
===============================================================
LIA EmployX

CV Section Splitter

Divide un CV en secciones para que cada extractor
reciba únicamente el texto que necesita.

Autor:
LIA EmployX Team
===============================================================
"""

from __future__ import annotations

import re


class CVSectionSplitter:

    """
    Divide un CV en bloques utilizando encabezados comunes.

    Devuelve un diccionario con las secciones encontradas.
    """

    def __init__(self):

        self.patterns = {

            "experience": [

                r"experience",
                r"work experience",
                r"professional experience",
                r"employment",
                r"historial laboral",
                r"experiencia",
                r"experiencia laboral"

            ],

            "education": [

                r"education",
                r"academic",
                r"academic background",
                r"formación",
                r"educación",
                r"estudios"

            ],

            "skills": [

                r"skills",
                r"technical skills",
                r"competencies",
                r"habilidades",
                r"competencias",
                r"tecnologías"

            ],

            "languages": [

                r"languages",
                r"idiomas"

            ],

            "certifications": [

                r"certifications",
                r"licenses",
                r"certificados",
                r"certificaciones"

            ],

            "projects": [

                r"projects",
                r"portfolio",
                r"proyectos",
                r"portafolio"

            ]

        }

    # =====================================================

    def split(self, text: str):

        text = text.replace("\r\n", "\n")

        lines = text.split("\n")

        sections = {

            "personal_info": [],

            "experience": [],

            "education": [],

            "skills": [],

            "languages": [],

            "certifications": [],

            "projects": []

        }

        current = "personal_info"

        for line in lines:

            clean = line.strip()

            lower = clean.lower()

            found = False

            for section, keywords in self.patterns.items():

                for keyword in keywords:

                    if re.fullmatch(keyword, lower):

                        current = section

                        found = True

                        break

                if found:

                    break

            sections[current].append(line)

        return {

            key: "\n".join(value).strip()

            for key, value in sections.items()

        }

    # =====================================================

    def print_summary(self, sections):

        print()

        print("=" * 70)

        print("CV Sections")

        print("=" * 70)

        print()

        for name, content in sections.items():

            print(

                f"{name:20}"

                f"{len(content):6}"

                f" caracteres"

            )

        print()