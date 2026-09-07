from dataclasses import dataclass, field


@dataclass
class Experience:

    company: str = ""

    position: str = ""

    start_date: str = ""

    end_date: str = ""

    location: str = ""

    description: str = ""
    employment_type: str = ""
    current: bool = False
    achievements: list[str] = field(default_factory=list)
