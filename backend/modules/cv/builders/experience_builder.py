import re
from typing import List
from backend.modules.cv.builders.base_builder import BaseBuilder, BuildResult
from backend.modules.cv.models.cv_experience import CVExperience

from backend.modules.cv.drafts.experience_draft import ExperienceDraft
from backend.modules.cv.normalizers.experience_normalizer import ExperienceNormalizer

class ExperienceBuilder(BaseBuilder[List[CVExperience]]):
    def build(self, text: str) -> BuildResult[List[CVExperience]]:
        warnings = []
        confidence = 0.0
        if not text.strip():
            warnings.append("Sección de experiencia vacía.")
            return BuildResult(data=[], confidence=0.0, warnings=warnings)
            
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        date_pattern = re.compile(r"((?:19|20)\d{2})\s*[-–—a]\s*((?:19|20)\d{2}|presente|actualidad|present|now|current)", re.IGNORECASE)
        
        def is_header(l: str) -> bool:
            clean = re.sub(r'[^a-z]', '', l.lower())
            return clean in ("experience", "featuredexperience", "workexperience", "experiencia", "experienciaprofesional", "professionalexperience")
            
        blocks = []
        current_block = []
        
        for line in lines:
            if is_header(line):
                continue
                
            is_date_line = bool(date_pattern.search(line))
            
            if is_date_line:
                if current_block:
                    # The line immediately before the date line usually belongs to the new experience (Position)
                    prev_line = current_block.pop()
                    if current_block:
                        blocks.append(current_block)
                    current_block = [prev_line, line]
                else:
                    current_block.append(line)
            else:
                current_block.append(line)
                
        if current_block:
            blocks.append(current_block)
            
        experiences = []
        
        # Deduplication tracker
        seen_drafts = set()
        
        for block_lines in blocks:
            if not block_lines:
                continue
                
            title_line = block_lines[0]
            date_line = ""
            start_date = ""
            end_date = ""
            
            # Check if line 0 or 1 has dates
            date_match = date_pattern.search(title_line)
            if date_match:
                start_date = date_match.group(1)
                end_date = date_match.group(2)
                # Keep title_line as is, normalizer will handle
            elif len(block_lines) > 1:
                date_line = block_lines[1]
                date_match = date_pattern.search(date_line)
                if date_match:
                    start_date = date_match.group(1)
                    end_date = date_match.group(2)
                    
                    company_str = date_line[:date_match.start()].strip()
                    # Clean up trailing punctuation if any
                    company_str = re.sub(r'[-–—\|,]$', '', company_str).strip()
                    
                    if company_str:
                        # Prevent normalizer from splitting inside the company name
                        company_safe = re.sub(r'[-–—\|]', ' ', company_str)
                        title_line = f"{company_safe} | {title_line}"
                    
            desc_start = 2 if (date_line and date_match) else 1
            description = "\n".join(block_lines[desc_start:])
            
            draft_key = (title_line, start_date, end_date, description)
            if draft_key in seen_drafts:
                continue
            seen_drafts.add(draft_key)
            
            draft = ExperienceDraft(
                raw_title_line=title_line,
                raw_start_date=start_date,
                raw_end_date=end_date,
                raw_description=description
            )
            
            norm_res = ExperienceNormalizer.normalize(draft)
            experiences.append(norm_res.data)
            confidence += norm_res.confidence
            warnings.extend(norm_res.warnings)
            
        final_confidence = (confidence / len(experiences)) if experiences else 40.0
        warnings.append("Agrupación por anclas de fecha aplicada.")
        
        return BuildResult(data=experiences, confidence=final_confidence, warnings=warnings)
