"""Validate nested profile types; defaults represent missing information."""
from dataclasses import asdict
from backend.modules.cv.parser.profile_mapper import ProfileMapper


class CVValidator:
    def validate(self, data: dict) -> dict:
        if not isinstance(data, dict):
            raise ValueError("La IA no devolvió un objeto JSON.")
        return asdict(ProfileMapper().map(data))
