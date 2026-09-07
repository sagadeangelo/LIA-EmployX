"""API envelopes; profile fields reuse the domain dataclasses."""
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator
from backend.modules.cv.domain.professional_profile import ProfessionalProfile


class ProfileDraft(BaseModel):
    model_config = ConfigDict(extra='forbid', allow_inf_nan=False)
    title: str = Field(min_length=1, max_length=160)
    profile: ProfessionalProfile
    source_text: str = Field(default='', max_length=60000)
    extraction_method: Literal['local', 'lmstudio'] = 'local'
    warnings: list[str] = Field(default_factory=list, max_length=20)

    @field_validator('title')
    @classmethod
    def nonblank_title(cls, value):
        value = value.strip()
        if not value:
            raise ValueError('El nombre del CV no puede estar vacío.')
        return value

    @field_validator('profile')
    @classmethod
    def valid_numbers(cls, profile):
        import math
        numbers = [skill.years for skill in profile.skills]
        numbers.append(profile.preferences.desired_salary)
        numbers.extend(item.confidence for item in profile.certifications)
        if any(number is not None and (not math.isfinite(number) or number < 0) for number in numbers):
            raise ValueError('Los campos numéricos deben ser finitos y no negativos.')
        return profile
