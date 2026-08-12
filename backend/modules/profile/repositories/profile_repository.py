import json
import os
from typing import List, Optional
from backend.modules.profile.models.professional_profile import ProfessionalProfile

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "data")
os.makedirs(DB_DIR, exist_ok=True)
PROFILE_DB = os.path.join(DB_DIR, "profiles.json")

class ProfileRepository:
    def __init__(self):
        if not os.path.exists(PROFILE_DB):
            with open(PROFILE_DB, "w", encoding="utf-8") as f:
                json.dump([], f)

    def _load(self) -> List[dict]:
        with open(PROFILE_DB, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self, data: List[dict]):
        with open(PROFILE_DB, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)

    def save(self, profile: ProfessionalProfile) -> ProfessionalProfile:
        data = self._load()
        profile_dict = profile.model_dump(mode="json")
        
        # Check if exists to update
        for i, existing in enumerate(data):
            if existing.get("id") == profile.id:
                data[i] = profile_dict
                self._save(data)
                return profile
                
        # If not, append
        data.append(profile_dict)
        self._save(data)
        return profile

    def get_by_id(self, profile_id: str) -> Optional[ProfessionalProfile]:
        data = self._load()
        for item in data:
            if item.get("id") == profile_id:
                return ProfessionalProfile.model_validate(item)
        return None

    def get_all(self) -> List[ProfessionalProfile]:
        data = self._load()
        return [ProfessionalProfile.model_validate(item) for item in data]
