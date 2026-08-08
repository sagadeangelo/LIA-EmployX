import logging
from typing import Dict, Any
from backend.modules.cv.models.cv_document import CVDocument
from backend.modules.cv.models.cv_metadata import CVMetadata
from backend.modules.cv.language.language_result import LanguageResult

from .personal_info_builder import PersonalInfoBuilder
from .experience_builder import ExperienceBuilder
from .education_builder import EducationBuilder
from .skills_builder import SkillsBuilder
from .languages_builder import LanguagesBuilder
from .certifications_builder import CertificationsBuilder

logger = logging.getLogger(__name__)

class CVDocumentBuilder:
    """
    Orchestrates the construction of a CVDocument from a SectionMap.
    Delegates parsing to specialized builders.
    """
    def __init__(self):
        self.personal_info_builder = PersonalInfoBuilder()
        self.experience_builder = ExperienceBuilder()
        self.education_builder = EducationBuilder()
        self.skills_builder = SkillsBuilder()
        self.languages_builder = LanguagesBuilder()
        self.certifications_builder = CertificationsBuilder()

    def build(self, metadata: CVMetadata, raw_text: str, sections: Dict[str, Any], language: LanguageResult) -> CVDocument:
        logger.info("CVDocumentBuilder: Iniciando construcción del CVDocument")
        
        def get_text(key: str) -> str:
            val = sections.get(key)
            if hasattr(val, "text"):
                return val.text
            return str(val) if val else ""
            
        # Build individual sections
        personal_info_result = self.personal_info_builder.build(get_text("personal_info"))
        experience_result = self.experience_builder.build(get_text("experience"))
        education_result = self.education_builder.build(get_text("education"))
        skills_result = self.skills_builder.build(get_text("skills"))
        languages_result = self.languages_builder.build(get_text("languages"))
        certifications_result = self.certifications_builder.build(get_text("certifications"))
        
        # Log warnings and confidence
        self._log_result("PersonalInfo", personal_info_result)
        self._log_result("Experience", experience_result)
        self._log_result("Education", education_result)
        
        # For professional summary, simply use the summary section text
        summary_text = get_text("summary").strip()
        
        clean_sections = {k: get_text(k) for k in sections.keys()}
        
        document = CVDocument(
            metadata=metadata,
            raw_text=raw_text,
            cleaned_text=raw_text,
            sections=clean_sections,
            detected_language=language,
            contact=personal_info_result.data,
            professional_summary=summary_text,
            experiences=experience_result.data,
            education=education_result.data,
            skills=skills_result.data,
            languages=languages_result.data,
            certifications=certifications_result.data
        )
        
        return document

    def _log_result(self, name: str, result):
        if result.warnings:
            logger.warning(f"CVDocumentBuilder [{name}]: Confidence {result.confidence}% - {result.warnings}")
