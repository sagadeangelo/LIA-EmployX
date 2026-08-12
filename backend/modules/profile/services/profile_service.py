from typing import Optional, List
from backend.modules.profile.repositories.profile_repository import ProfileRepository
from backend.modules.profile.models.professional_profile import ProfessionalProfile

class ProfileService:
    def __init__(self, repository: ProfileRepository):
        self.repository = repository
        
    def get_profile(self, profile_id: str) -> Optional[ProfessionalProfile]:
        return self.repository.get_by_id(profile_id)
        
    def save_profile(self, profile: ProfessionalProfile) -> ProfessionalProfile:
        return self.repository.save(profile)
