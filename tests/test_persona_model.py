import pytest
from src.models.persona import SwissPersona, ExperienceEntry

def test_persona_basic():
    p = SwissPersona(
        first_name='Anna',
        last_name='Mueller',
        birth_year=1990,
        canton='ZH',
        language='de',
        experiences=[
            ExperienceEntry(title='Software Engineer', start_year=2015, end_year=2020)
        ]
    )
    assert p.age >= 30
    assert p.total_experience_years() == 5

def test_invalid_canton():
    with pytest.raises(ValueError):
        SwissPersona(first_name='X', last_name='Y', birth_year=1990, canton='XX', language='de')
