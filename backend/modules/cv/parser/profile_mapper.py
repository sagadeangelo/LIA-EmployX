"""Validate and map extracted or user-edited data without guessing values."""
from pydantic import TypeAdapter
from backend.modules.cv.domain.professional_profile import ProfessionalProfile

PROFILE_ADAPTER = TypeAdapter(ProfessionalProfile)


class ProfileMapper:
    def map(self, data: dict) -> ProfessionalProfile:
        return PROFILE_ADAPTER.validate_python(data)
