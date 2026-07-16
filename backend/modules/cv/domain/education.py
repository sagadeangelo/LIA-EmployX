"""
===============================================================
LIA EmployX

Education

Modelo de formación académica.

Autor:
LIA EmployX Team
===============================================================
"""

from dataclasses import dataclass


@dataclass(slots=True)
class Education:

    institution: str = ""

    degree: str = ""

    field_of_study: str = ""

    start_date: str = ""

    end_date: str = ""

    current: bool = False

    description: str = ""

    location: str = ""

    grade: str = ""