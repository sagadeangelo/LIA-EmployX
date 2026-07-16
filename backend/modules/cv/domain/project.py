from dataclasses import dataclass


@dataclass
class Project:

    name: str = ""

    description: str = ""

    technologies: list[str] | None = None

    url: str = ""