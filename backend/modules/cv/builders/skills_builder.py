import re
from typing import List
from backend.modules.cv.builders.base_builder import BaseBuilder, BuildResult
from backend.modules.cv.models.cv_skill import CVSkill

class SkillsBuilder(BaseBuilder[List[CVSkill]]):
    # Known sub-section headers that appear inside the skills section
    _SECTION_HEADERS = {
        "coretechnologies", "coretech", "skills", "habilidades",
        "technologies", "tecnologias", "tools", "herramientas",
        "liaecosystem", "ecosistema", "frameworks", "softskills",
        "hardskills", "competencias", "aiskillset", "aitoolkit",
        "aitoolset", "toolkit",
    }
    
    def build(self, text: str) -> BuildResult[List[CVSkill]]:
        warnings = []
        if not text.strip():
            warnings.append("Sección de habilidades vacía.")
            return BuildResult(data=[], confidence=0.0, warnings=warnings)
            
        def is_header(s: str) -> bool:
            clean = re.sub(r'[^a-z]', '', s.lower())
            return clean in self._SECTION_HEADERS

        # Split by commas, bullets, newlines, and ·
        cleaned_text = re.sub(r'[•►▪◆★⭐✓✔—·\n]', ',', text)
        raw_skills = [s.strip() for s in cleaned_text.split(',') if s.strip()]
        
        # Filter headers and deduplicate while preserving order
        seen = set()
        unique_skills = []
        for s in raw_skills:
            # Skip if looks like a section header
            if is_header(s):
                continue
            # Skip lines that contain "Technologies:" prefix from the LIA Ecosystem block
            if re.match(r'^technologies\s*:', s, re.IGNORECASE):
                # Extract the skills after the colon
                after = re.sub(r'^technologies\s*:', '', s, flags=re.IGNORECASE).strip()
                sub_skills = [x.strip() for x in re.split(r'[·,]', after) if x.strip()]
                for sub in sub_skills:
                    lower_s = sub.lower()
                    if lower_s not in seen and len(sub) > 1:
                        seen.add(lower_s)
                        unique_skills.append(sub)
                continue
            lower_s = s.lower()
            if lower_s not in seen and len(s) > 1:
                seen.add(lower_s)
                unique_skills.append(s)
                
        skills_list = []
        for skill in unique_skills:
            skills_list.append(CVSkill(name=skill, category="Technical", source="Skills"))
            
        confidence = 70.0
        if not skills_list:
            warnings.append("No se extrajeron habilidades reconocibles.")
            
        return BuildResult(data=skills_list, confidence=confidence, warnings=warnings)
