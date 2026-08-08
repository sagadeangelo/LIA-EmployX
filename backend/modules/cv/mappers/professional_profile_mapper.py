from backend.modules.cv.models.cv_document import CVDocument
from backend.modules.profile.models.professional_profile import (
    ProfessionalProfile,
    PersonalInfo,
    Experience,
    Education,
    Skills,
    Language,
    Certification
)

class ProfessionalProfileMapper:
    """
    Mapper class responsible for converting a CVDocument (extraction layer)
    into a ProfessionalProfile (canonical business entity).
    """

    @staticmethod
    def from_cv_document(document: CVDocument) -> ProfessionalProfile:
        profile = ProfessionalProfile()

        # Map Personal Info
        profile.personal_info = PersonalInfo(
            name=document.contact.full_name or "",
            email=document.contact.email or "",
            phone=document.contact.phone or "",
            location=document.contact.location or "",
            linkedin=document.contact.linkedin or "",
            portfolio=document.contact.portfolio or "",
            website=document.contact.website or "",
            professional_summary=document.professional_summary or "",
            # Let the CareerAgent figure out the career_goal and current_position later if needed,
            # but we can try to default to the first experience role for current_position
            current_position=document.experiences[0].role if document.experiences else "",
            # Calculate years of experience roughly based on experiences or let it be 0 for now
            years_of_experience=0  
        )

        # Map Experience
        mapped_experiences = []
        for exp in document.experiences:
            mapped_experiences.append(
                Experience(
                    company=exp.company or "",
                    role=exp.role or "",
                    start_date=exp.start_date or "",
                    end_date=exp.end_date or "",
                    description=exp.description or "",
                    achievements=exp.achievements or [],
                    technologies=exp.technologies or [],
                    skills_used=exp.skills_used or []
                )
            )
        profile.experience = mapped_experiences

        # Map Education
        mapped_education = []
        for edu in document.education:
            mapped_education.append(
                Education(
                    institution=edu.institution or "",
                    degree=edu.degree or "",
                    level=edu.level or "",
                    period=edu.period or ""
                )
            )
        profile.education = mapped_education

        # Map Skills
        # CVDocument has list of CVSkill, ProfessionalProfile has a Skills class
        # Let's categorize them or just dump them in technical_skills for now
        technical_skills = []
        soft_skills = []
        for skill in document.skills:
            if skill.category.lower() == "soft":
                soft_skills.append(skill.name)
            else:
                technical_skills.append(skill.name)
                
        profile.skills = Skills(
            technical_skills=technical_skills,
            soft_skills=soft_skills
        )

        # Map Languages
        mapped_languages = []
        for lang in document.languages:
            mapped_languages.append(
                Language(
                    language=lang.language or "",
                    level=lang.level or "",
                    certification=lang.certification or ""
                )
            )
        profile.languages = mapped_languages

        # Map Certifications
        # CVDocument certifications is just list of str, we map to Certification object
        mapped_certifications = []
        for cert_name in document.certifications:
            mapped_certifications.append(
                Certification(
                    name=cert_name,
                    provider="",
                    date=""
                )
            )
        profile.certifications = mapped_certifications
        
        return profile
