"""
===============================================================
LIA EmployX

Parser Orchestrator

Orquesta todos los extractores del CV.

Responsabilidades

• Dividir el CV en secciones
• Ejecutar cada extractor
• Construir ProfessionalProfile

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

from backend.modules.cv.parser.cv_section_splitter import CVSectionSplitter

from backend.modules.cv.parser.extractors.personal_info_extractor import (
    PersonalInfoExtractor,
)

from backend.modules.cv.parser.extractors.experience_extractor import (
    ExperienceExtractor,
)

from backend.modules.cv.parser.extractors.education_extractor import (
    EducationExtractor,
)

from backend.modules.cv.parser.extractors.skills_extractor import (
    SkillsExtractor,
)

from backend.modules.cv.parser.extractors.languages_extractor import (
    LanguagesExtractor,
)

from backend.modules.cv.parser.extractors.certifications_extractor import (
    CertificationsExtractor,
)

from backend.modules.cv.parser.extractors.projects_extractor import (
    ProjectsExtractor,
)


class ParserOrchestrator:

    """
    Parser inteligente basado en extractores especializados.
    """

    def __init__(self):

        self.splitter = CVSectionSplitter()

        self.personal = PersonalInfoExtractor()

        self.experience = ExperienceExtractor()

        self.education = EducationExtractor()

        self.skills = SkillsExtractor()

        self.languages = LanguagesExtractor()

        self.certifications = CertificationsExtractor()

        self.projects = ProjectsExtractor()

    # ---------------------------------------------------------

    def parse(self, cv_text: str) -> ProfessionalProfile:

        print()

        print("=" * 70)
        print("Parser Orchestrator")
        print("=" * 70)

        # =====================================================
        # Dividir CV
        # =====================================================

        sections = self.splitter.split(cv_text)

        self.splitter.print_summary(sections)

        profile = ProfessionalProfile()

        # =====================================================
        # Personal Info
        # =====================================================

        print("Extrayendo información personal...")

        try:

            data = self.personal.extract(

                sections["personal_info"]

            )

            profile.personal_info = PersonalInfo(**data)

        except Exception as e:

            print(f"⚠ Personal Info: {e}")

        # =====================================================
        # Experience
        # =====================================================

        print("Extrayendo experiencia...")

        try:

            items = self.experience.extract(

                sections["experience"]

            )

            profile.experience = [

                Experience(**item)

                for item in items

            ]

        except Exception as e:

            print(f"⚠ Experience: {e}")

        # =====================================================
        # Education
        # =====================================================

        print("Extrayendo educación...")

        try:

            items = self.education.extract(

                sections["education"]

            )

            profile.education = [

                Education(**item)

                for item in items

            ]

        except Exception as e:

            print(f"⚠ Education: {e}")

        # =====================================================
        # Skills
        # =====================================================

        print("Extrayendo habilidades...")

        try:

            items = self.skills.extract(

                sections["skills"]

            )

            profile.skills = [

                Skill(**item)

                for item in items

            ]

        except Exception as e:

            print(f"⚠ Skills: {e}")

        # =====================================================
        # Languages
        # =====================================================

        print("Extrayendo idiomas...")

        try:

            items = self.languages.extract(

                sections["languages"]

            )

            profile.languages = [

                Language(**item)

                for item in items

            ]

        except Exception as e:

            print(f"⚠ Languages: {e}")

        # =====================================================
        # Certifications
        # =====================================================

        print("Extrayendo certificaciones...")

        try:

            items = self.certifications.extract(

                sections["certifications"]

            )

            profile.certifications = [

                Certification(**item)

                for item in items

            ]

        except Exception as e:

            print(f"⚠ Certifications: {e}")

        # =====================================================
        # Projects
        # =====================================================

        print("Extrayendo proyectos...")

        try:

            items = self.projects.extract(

                sections["projects"]

            )

            profile.projects = [

                Project(**item)

                for item in items

            ]

        except Exception as e:

            print(f"⚠ Projects: {e}")

        print()

        print("=" * 70)
        print("Parsing finalizado")
        print("=" * 70)
        print()

        return profile