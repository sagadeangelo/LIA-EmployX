"""
===============================================================
LIA EmployX

Professional Profile

Representa el perfil profesional completo de un usuario.
===============================================================
"""

from dataclasses import dataclass, field

from .personal_info import PersonalInfo
from .experience import Experience
from .education import Education
from .certification import Certification
from .language import Language
from .skill import Skill
from .project import Project
from .social_links import SocialLinks
from .preferences import Preferences


@dataclass
class ProfessionalProfile:

    # --------------------------------------------------------
    # Información personal
    # --------------------------------------------------------

    personal_info: PersonalInfo = field(
        default_factory=PersonalInfo
    )

    # --------------------------------------------------------
    # Experiencia laboral
    # --------------------------------------------------------

    experience: list[Experience] = field(
        default_factory=list
    )

    # --------------------------------------------------------
    # Educación
    # --------------------------------------------------------

   