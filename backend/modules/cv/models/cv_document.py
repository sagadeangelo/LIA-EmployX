from pydantic import BaseModel, Field

from backend.modules.cv.language.language_result import LanguageResult
from backend.modules.cv.models.cv_certification import CVCertification
from backend.modules.cv.models.cv_contact import CVContact
from backend.modules.cv.models.cv_education import CVEducation
from backend.modules.cv.models.cv_experience import CVExperience
from backend.modules.cv.models.cv_language import CVLanguage
from backend.modules.cv.models.cv_metadata import CVMetadata
from backend.modules.cv.models.cv_skill import CVSkill


class CVDocument(BaseModel):
    """
    Canonical representation of a candidate.

    Every AI Agent inside LIA EmployX works over this object.

    The model intentionally keeps different types of professional
    information separated so downstream agents can reason over
    education, continuous training, certifications, skills and
    experience independently.
    """

    # ==========================================================
    # DOCUMENT
    # ==========================================================

    metadata: CVMetadata

    detected_language: LanguageResult | None = None

    # ==========================================================
    # PERSONAL INFORMATION
    # ==========================================================

    contact: CVContact = Field(
        default_factory=CVContact
    )

    professional_summary: str = ""

    # ==========================================================
    # CAREER
    # ==========================================================

    experiences: list[CVExperience] = Field(
        default_factory=list
    )

    # Formal academic education.
    education: list[CVEducation] = Field(
        default_factory=list
    )

    # Courses, ongoing professional development and other
    # non-formal / continuing education.
    continuous_training: list[CVEducation] = Field(
        default_factory=list
    )

    skills: list[CVSkill] = Field(
        default_factory=list
    )

    languages: list[CVLanguage] = Field(
        default_factory=list
    )

    certifications: list[CVCertification] = Field(
        default_factory=list
    )

    projects: list[str] = Field(
        default_factory=list
    )

    achievements: list[str] = Field(
        default_factory=list
    )

    # ==========================================================
    # RAW DOCUMENT
    # ==========================================================

    raw_text: str = ""

    cleaned_text: str = ""

    sections: dict[str, str] = Field(
        default_factory=dict
    )

    # ==========================================================
    # ANALYSIS
    # ==========================================================

    ats_score: float | None = None

    detected_keywords: list[str] = Field(
        default_factory=list
    )

    missing_keywords: list[str] = Field(
        default_factory=list
    )

    recommendations: list[str] = Field(
        default_factory=list
    )

    warnings: list[str] = Field(
        default_factory=list
    )