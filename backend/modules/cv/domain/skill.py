from dataclasses import dataclass


@dataclass
class Skill:

    name: str = ""

    level: str = ""

    years: float | None = None