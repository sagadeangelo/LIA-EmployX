import re
from backend.modules.cv.drafts.experience_draft import ExperienceDraft
from backend.modules.cv.models.cv_experience import CVExperience
from backend.modules.cv.models.partial_date import PartialDate, DatePrecision
from backend.modules.cv.normalizers.normalization_result import NormalizationResult

class ExperienceNormalizer:
    @classmethod
    def normalize(cls, draft: ExperienceDraft) -> NormalizationResult[CVExperience]:
        warnings = []
        confidence = 100.0
        
        # Normalize Company and Position
        # Commonly separated by —, -, |, or ,
        company = draft.raw_title_line
        position = "No encontrado"
        
        # Try to split by common separators
        sep_match = re.split(r'\s*(?:[-–—\|]|\b(?:como|as)\b)\s*', draft.raw_title_line, maxsplit=1)
        if len(sep_match) == 2:
            company = sep_match[0].strip()
            position = sep_match[1].strip()
            
            # Clean up trailing dates from position if regex missed it
            position = re.sub(r'\s*\(\s*(?:19|20)\d{2}.*', '', position).strip()
        else:
            warnings.append("Position inferred as missing/combined with company.")
            confidence -= 20.0
            
        if position == "No encontrado" or not position:
            position = "Desconocido" # Pydantic requires str, not None.
            
        # Normalize Dates
        start_date = cls._parse_date(draft.raw_start_date)
        
        is_current = False
        end_date = None
        if re.search(r'(presente|actual|present|now)', draft.raw_end_date, re.IGNORECASE):
            is_current = True
            warnings.append("End date interpreted as Present")
        else:
            end_date = cls._parse_date(draft.raw_end_date)
            
        exp = CVExperience(
            company=company,
            position=position,
            start_date=start_date,
            end_date=end_date,
            is_current=is_current,
            description=draft.raw_description,
            achievements=[],
            technologies=[],
            skills=[]
        )
        
        return NormalizationResult(
            data=exp,
            confidence=confidence,
            warnings=warnings
        )
        
    @classmethod
    def _parse_date(cls, raw: str) -> PartialDate | None:
        if not raw:
            return None
            
        # Very naive YEAR parser just for the example to work
        # If it says "2021", extract year
        year_match = re.search(r'\b((?:19|20)\d{2})\b', raw)
        if year_match:
            return PartialDate(
                year=int(year_match.group(1)),
                precision=DatePrecision.YEAR
            )
            
        return None
