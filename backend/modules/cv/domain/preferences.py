from dataclasses import dataclass


@dataclass
class Preferences:

    desired_salary: float | None = None

    preferred_country: str = ""

    preferred_city: str = ""

    remote_only: bool = False

    relocation: bool = False