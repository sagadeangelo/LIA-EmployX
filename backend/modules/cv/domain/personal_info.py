from dataclasses import dataclass


@dataclass
class PersonalInfo:

    first_name: str = ""

    last_name: str = ""

    full_name: str = ""

    email: str = ""

    phone: str = ""

    city: str = ""

    state: str = ""

    country: str = ""

    address: str = ""