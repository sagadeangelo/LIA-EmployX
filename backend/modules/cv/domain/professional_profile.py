"""Canonical, serializable profile shared by the API and CV agent."""
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
    personal_info: PersonalInfo = field(default_factory=PersonalInfo)
    summary: str = ""
    experience: list[Experience] = field(default_factory=list)
    education: list[Education] = field(default_factory=list)
    skills: list[Skill] = field(default_factory=list)
    languages: list[Language] = field(default_factory=list)
    certifications: list[Certification] = field(default_factory=list)
    projects: list[Project] = field(default_factory=list)
    social_links: SocialLinks = field(default_factory=SocialLinks)
    preferences: Preferences = field(default_factory=Preferences)
