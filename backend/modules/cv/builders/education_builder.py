import re
from typing import List
from backend.modules.cv.builders.base_builder import BaseBuilder, BuildResult
from backend.modules.cv.models.cv_education import CVEducation

class EducationBuilder(BaseBuilder[List[CVEducation]]):
    def build(self, text: str) -> BuildResult[List[CVEducation]]:
        warnings = []
        if not text.strip():
            warnings.append("Sección de educación vacía.")
            return BuildResult(data=[], confidence=0.0, warnings=warnings)
            
        def is_header(l: str) -> bool:
            clean = re.sub(r'[^a-z]', '', l.lower())
            return clean in ("education", "educacion", "educación", "academicbackground", "formacionacademica")

        # Basic deterministic logic: Split by double newlines to identify education blocks
        blocks = re.split(r'\n\s*\n', text.strip())
        education_list = []
        seen_educations = set()
        
        for block in blocks:
            if not block.strip():
                continue
                
            lines = [line.strip() for line in block.split('\n') if line.strip()]
            if not lines:
                continue
                
            # Ignore headers
            if is_header(lines[0]) and len(lines) == 1:
                continue
                
            title_line = lines[0]
            if is_header(title_line):
                title_line = lines[1] if len(lines) > 1 else ""
                lines = lines[1:]
                
            if not title_line:
                continue
                
            degree = lines[1] if len(lines) > 1 else ""
            
            # Extract year if possible
            date_match = re.search(r"((?:19|20)\d{2})", block)
            period = date_match.group(1) if date_match else ""
            
            # Handle merged degree and institution on the same line
            if not degree:
                # Look for a lowercase letter followed by a capital letter that starts an institution word
                merged_match = re.search(r'([a-z])(University|Universidad|College|Institute|Instituto|Coursera|Udemy|Platzi|School)', title_line)
                if merged_match:
                    degree = title_line[:merged_match.start(1)+1].strip()
                    institution = title_line[merged_match.start(2):].strip()
                    title_line = institution
                else:
                    # Check | separator
                    parts = [p.strip() for p in title_line.split('|')]
                    if len(parts) == 2:
                        part1, part2 = parts
                        if any(x in part2.lower() for x in ['university', 'universidad', 'college', 'instituto', 'coursera', 'udemy']):
                            title_line = part2
                            degree = part1
                        else:
                            title_line = part1
                            degree = part2
                    elif ":" in title_line:
                        # e.g. "Continuous Training in:Artificial Intelligence..."
                        parts = [p.strip() for p in title_line.split(':', 1)]
                        title_line = parts[0]
                        degree = parts[1]
                        
            # Use title_line as institution
            institution = title_line
            
            edu_key = (institution, degree, period)
            if edu_key in seen_educations:
                continue
            seen_educations.add(edu_key)
            
            education_list.append(
                CVEducation(
                    institution=institution,
                    degree=degree,
                    level="",
                    period=period
                )
            )
            
        confidence = 70.0
        warnings.append("Agrupación y separación heurística aplicada.")
        
        return BuildResult(data=education_list, confidence=confidence, warnings=warnings)
