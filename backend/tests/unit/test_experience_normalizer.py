import pytest
from backend.modules.cv.drafts.experience_draft import ExperienceDraft
from backend.modules.cv.normalizers.experience_normalizer import ExperienceNormalizer
from backend.modules.cv.models.partial_date import DatePrecision

def test_experience_normalizer_basic():
    draft = ExperienceDraft(
        raw_title_line="Empresa Alpha — Senior Flutter Developer",
        raw_start_date="2021",
        raw_end_date="presente",
        raw_description="Desarrollo de apps multiplataforma"
    )
    
    result = ExperienceNormalizer.normalize(draft)
    
    assert result.confidence == 100.0
    assert "End date interpreted as Present" in result.warnings
    
    exp = result.data
    assert exp.company == "Empresa Alpha"
    assert exp.position == "Senior Flutter Developer"
    assert exp.is_current is True
    assert exp.end_date is None
    
    assert exp.start_date is not None
    assert exp.start_date.year == 2021
    assert exp.start_date.precision == DatePrecision.YEAR
    assert exp.start_date.month is None

def test_experience_normalizer_inferred_position():
    draft = ExperienceDraft(
        raw_title_line="Freelance Developer",
        raw_start_date="2020",
        raw_end_date="2022",
        raw_description="Desarrollo web"
    )
    
    result = ExperienceNormalizer.normalize(draft)
    
    assert result.confidence == 80.0
    assert "Position inferred as missing/combined with company." in result.warnings
    
    exp = result.data
    assert exp.company == "Freelance Developer"
    assert exp.position == "Desconocido"
    assert exp.is_current is False
    assert exp.end_date is not None
    assert exp.end_date.year == 2022
