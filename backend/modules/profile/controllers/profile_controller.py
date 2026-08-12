from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from backend.modules.profile.services.profile_service import ProfileService
from backend.modules.profile.repositories.profile_repository import ProfileRepository
from backend.modules.profile.models.professional_profile import ProfessionalProfile

router = APIRouter(prefix="/api/v1/profile", tags=["Profile"])

def get_profile_service() -> ProfileService:
    repo = ProfileRepository()
    return ProfileService(repo)

@router.get("/{profile_id}", response_model=ProfessionalProfile)
async def get_profile(profile_id: str, profile_service: ProfileService = Depends(get_profile_service)):
    profile = profile_service.get_profile(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile
