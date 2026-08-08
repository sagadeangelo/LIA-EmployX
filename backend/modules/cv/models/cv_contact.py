from __future__ import annotations

from pydantic import BaseModel, EmailStr


class CVContact(BaseModel):
    """
    Información de contacto detectada en el CV.
    """

    full_name: str | None = None

    email: EmailStr | None = None

    phone: str | None = None

    location: str | None = None

    linkedin: str | None = None

    github: str | None = None

    portfolio: str | None = None

    website: str | None = None