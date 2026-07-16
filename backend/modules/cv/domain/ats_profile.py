"""
===============================================================
LIA EmployX

ATS Profile

Representación optimizada de un candidato para motores ATS.

Este perfil NO proviene directamente del CV.

Se construye a partir del ProfessionalProfile mediante IA.

Autor:
LIA EmployX Team
===============================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class ATSProfile:
    """
    Perfil optimizado para búsquedas ATS.

    Es generado por IA a partir del ProfessionalProfile.
    """

    # ---------------------------------------------------------
    # Clasificación principal
    # ---------------------------------------------------------

    primary_role: str = ""

    secondary_roles: list[str] = field(default_factory=list)

    industry: str = ""

    seniority: str = ""

    experience_level: str = ""

    estimated_years: float = 0.0

    # ---------------------------------------------------------
    # Competencias
    # ---------------------------------------------------------

    hard_skills: list[str] = field(default_factory=list)

    soft_skills: list[str] = field(default_factory=list)

    technical_stack: list[str] = field(default_factory=list)

    tools: list[str] = field(default_factory=list)

    # ---------------------------------------------------------
    # Áreas profesionales
    # ---------------------------------------------------------

    work_domains: list[str] = field(default_factory=list)

    job_titles: list[str] = field(default_factory=list)

    keywords: list[str] = field(default_factory=list)

    # ---------------------------------------------------------
    # Idiomas
    # ---------------------------------------------------------

    languages: list[str] = field(default_factory=list)

    # ---------------------------------------------------------
    # Disponibilidad
    # ---------------------------------------------------------

    remote: bool = False

    hybrid: bool = False

    onsite: bool = False

    relocation: bool = False

    travel: bool = False

    work_authorization: str = ""

    # ---------------------------------------------------------
    # Métricas IA
    # ---------------------------------------------------------

    confidence: float = 1.0

    parser_version: str = "1.0"

    # ---------------------------------------------------------
    # Utilidades
    # ---------------------------------------------------------

    def to_dict(self) -> dict:
        return self.__dict__

    @property
    def total_keywords(self) -> int:
        return len(self.keywords)

    @property
    def total_hard_skills(self) -> int:
        return len(self.hard_skills)

    @property
    def total_soft_skills(self) -> int:
        return len(self.soft_skills)

    @property
    def total_languages(self) -> int:
        return len(self.languages)

    def summary(self) -> str:
        return (
            f"Rol principal: {self.primary_role}\n"
            f"Industria: {self.industry}\n"
            f"Seniority: {self.seniority}\n"
            f"Años estimados: {self.estimated_years}\n"
            f"Hard Skills: {len(self.hard_skills)}\n"
            f"Soft Skills: {len(self.soft_skills)}\n"
            f"Keywords ATS: {len(self.keywords)}"
        )