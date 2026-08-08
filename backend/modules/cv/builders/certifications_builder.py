import re
from typing import List
from backend.modules.cv.builders.base_builder import BaseBuilder, BuildResult

class CertificationsBuilder(BaseBuilder[List[str]]):
    def build(self, text: str) -> BuildResult[List[str]]:
        warnings = []
        if not text.strip():
            warnings.append("Sección de certificaciones vacía.")
            return BuildResult(data=[], confidence=0.0, warnings=warnings)
            
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        cert_list = []
        
        for line in lines:
            line = re.sub(r'^[•►▪◆★⭐✓✔—\-\*]\s*', '', line)
            if line:
                cert_list.append(line)
                
        confidence = 80.0
        return BuildResult(data=cert_list, confidence=confidence, warnings=warnings)
