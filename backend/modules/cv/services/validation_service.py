import logging
from backend.modules.cv.models.cv_document import CVDocument

logger = logging.getLogger(__name__)

class ValidationService:
    """
    Validates and normalizes a built CVDocument before it is mapped to a ProfessionalProfile.
    """
    
    def validate(self, document: CVDocument) -> CVDocument:
        logger.info("ValidationService: Validating CVDocument")
        
        # Ensure email is lowercase
        if document.contact.email:
            document.contact.email = document.contact.email.lower().strip()
            
        # Deduplicate skills just in case
        seen = set()
        unique_skills = []
        for skill in document.skills:
            lower_name = skill.name.lower()
            if lower_name not in seen:
                seen.add(lower_name)
                unique_skills.append(skill)
        document.skills = unique_skills
        
        # Default missing values to prevent mapper crashes
        if not document.contact.full_name:
            document.contact.full_name = "Candidato Desconocido"
            
        return document
