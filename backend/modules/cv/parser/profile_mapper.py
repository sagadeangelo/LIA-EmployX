"""
===============================================================
LIA EmployX

Profile Mapper

Convierte el JSON validado en un ProfessionalProfile.

Autor:
LIA EmployX Team
===============================================================
"""

from __future__ import annotations

from backend.modules.cv.domain.professional_profile import ProfessionalProfile
from backend.modules.cv.domain.personal_info import PersonalInfo
from backend.modules.cv.domain.experience import Experience
from backend.modules.cv.domain.education import Education
from backend.modules.cv.domain.skill import Skill
from backend.modules.cv.domain.language import Language
from backend.modules.cv.domain.certification import Certification
from backend.modules.cv.domain.project import Project
from backend.modules.cv.domain.preferences import Preferences
from backend.modules.cv.domain.social_links import SocialLinks
from backend.modules.cv.domain.ats_profile import ATSProfile


class ProfileMapper:
    """
    Convierte un diccionario Python
    en un ProfessionalProfile.
    """

    # ==========================================================
    # API pública
    # ==========================================================

    def map(self, data: dict) -> ProfessionalProfile:

        profile = ProfessionalProfile()

        # ------------------------------------------------------
        # Personal
        # ------------------------------------------------------

        profile.personal_info = PersonalInfo(

            **data.get("personal_info", {})

        )

        # ------------------------------------------------------
        # Preferencias
        # ------------------------------------------------------

        profile.preferences = Preferences(

            **data.get("preferences", {})

        )

        # ------------------------------------------------------
        # Redes sociales
        # ------------------------------------------------------

        profile.social_links = SocialLinks(

            linkedin=data.get("personal_info", {}).get("linkedin", ""),

            github=data.get("personal_info", {}).get("github", ""),

            website=data.get("personal_info", {}).get("website", ""),

            portfolio=data.get("personal_info", {}).get("portfolio", "")

        )

        # ------------------------------------------------------
        # Experiencia
        # ------------------------------------------------------

        profile.experience = [

            Experience(**item)

            for item in data.get("experience", [])

        ]

        # ------------------------------------------------------
        # Educación
        # ------------------------------------------------------

        profile.education = [

            Education(**item)

            for item in data.get("education", [])

        ]

        # ------------------------------------------------------
        # Skills
        # ------------------------------------------------------

        profile.skills = [

            Skill(**item)

            for item in data.get("skills", [])

        ]

        # ------------------------------------------------------
        # Idiomas
        # ------------------------------------------------------

        profile.languages = [

            Language(**item)

            for item in data.get("languages", [])

        ]

        # ------------------------------------------------------
        # Certificaciones
        # ------------------------------------------------------

        profile.certifications = [

            Certification(**item)

            for item in data.get("certifications", [])

        ]

        # ------------------------------------------------------
        # Proyectos
        # ------------------------------------------------------

        profile.projects = [

            Project(**item)

            for item in data.get("projects", [])

        ]

        # ------------------------------------------------------
        # ATS
        # ------------------------------------------------------

        profile.ats_profile = ATSProfile(

            **data.get("ats", {})

        )

        return profile

    # ==========================================================
    # Utilidades
    # ==========================================================

    def summary(self, profile: ProfessionalProfile):

        print()

        print("=" * 70)

        print("Professional Profile")

        print("=" * 70)

        print()

        print("Nombre:")

        print(profile.personal_info.full_name)

        print()

        print("Experiencia:")

        print(len(profile.experience))

        print()

        print("Educación:")

        print(len(profile.education))

        print()

        print("Skills:")

        print(len(profile.skills))

        print()

        print("Idiomas:")

        print(len(profile.languages))

        print()

        print("Certificaciones:")

        print(len(profile.certifications))

        print()

        print("Proyectos:")

        print(len(profile.projects))

        print()


# ==============================================================
# Prueba local
# ==============================================================

if __name__ == "__main__":

    mapper = ProfileMapper()

    ejemplo = {

        "personal_info": {

            "full_name": "Miguel Tovar"

        }

    }

    profile = mapper.map(ejemplo)

    mapper.summary(profile)