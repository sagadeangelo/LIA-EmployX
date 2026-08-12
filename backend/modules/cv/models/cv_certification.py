from __future__ import annotations

from datetime import date

from pydantic import BaseModel


class CVCertification(BaseModel):
    """
    Represents a professional certification detected
    inside the candidate's CV.
    """

    name: str
    """
    Certification name.

    Example:
        AWS Certified Developer
        Google Data Analytics
        PMP
        Scrum Master
    """

    issuer: str | None = None
    """
    Organization that issued the certification.

    Example:
        Amazon
        Google
        Microsoft
        PMI
    """

    credential_id: str | None = None

    credential_url: str | None = None

    issue_date: date | None = None

    expiration_date: date | None = None

    never_expires: bool = False

    skills: list[str] = []

    verified: bool = False

    confidence: float = 1.0