"""Conservative offline extraction: literal email and explicitly labeled fields.

Other information remains in source_text for manual review. This is not AI.
"""
import re
from backend.modules.cv.domain.professional_profile import ProfessionalProfile


class LocalCVParser:
    def parse(self, text: str) -> ProfessionalProfile:
        profile = ProfessionalProfile()
        email = re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", text)
        if email:
            profile.personal_info.email = email.group(0)
        labels = {
            "nombre": "full_name", "nombre completo": "full_name", "name": "full_name",
            "teléfono": "phone", "telefono": "phone", "phone": "phone",
            "ciudad": "city", "city": "city", "país": "country", "pais": "country",
        }
        for line in text.splitlines():
            label, separator, value = line.partition(":")
            field = labels.get(label.strip().lower())
            if separator and field and value.strip():
                setattr(profile.personal_info, field, value.strip())
        return profile
