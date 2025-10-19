from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr, validator
import re
import datetime
import os

CURRENT_YEAR = datetime.date.today().year

class EducationEntry(BaseModel):
    institution: str
    degree: Optional[str] = None
    field: Optional[str] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None

class ExperienceEntry(BaseModel):
    title: str
    company: str
    canton: Optional[str] = None
    start_year: int
    end_year: Optional[int] = None
    description: Optional[str] = None
    seniority: Optional[str] = None

class SwissPersona(BaseModel):
    id: Optional[str] = Field(None, description="Unique id / uuid")
    first_name: str
    last_name: str
    gender: Optional[str] = Field(None, description="male/female/other/unknown")
    canton: str = Field(..., description="Swiss canton code, e.g. ZH, GE")
    language: str = Field(..., description="de/fr/it/en - main language of persona")
    age: int = Field(..., ge=16, le=100)
    birth_year: Optional[int] = None
    years_experience: int = Field(..., ge=0)
    seniority: Optional[str] = Field(None, description="junior,mid,senior,lead")
    industry: Optional[str] = None
    current_title: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    languages_spoken: List[str] = Field(default_factory=list)
    education: List[EducationEntry] = Field(default_factory=list)
    experience: List[ExperienceEntry] = Field(default_factory=list)
    summary: Optional[str] = None

    @validator('birth_year', always=True, pre=True)
    def set_birth_year_if_missing(cls, v, values):
        if v is not None:
            return v
        if 'age' in values and values['age'] is not None:
            return CURRENT_YEAR - values['age']
        return v

    @validator('years_experience')
    def experience_vs_age(cls, v, values):
        age = values.get('age')
        if age is not None:
            max_possible = max(0, age - 16)
            if v > max_possible:
                raise ValueError(f'years_experience ({v}) exceeds realistic max ({max_possible}) for age {age}')
        return v

    @validator('phone')
    def swiss_phone_pattern(cls, v):
        if v is None:
            return v
        # Accept +41 or leading 0. Swiss mobile prefixes typically 76-79
        pattern = re.compile(r'^(?:\+41|0)7[6-9]\d{7}$')
        if not pattern.match(v):
            raise ValueError("phone must match Swiss mobile pattern (e.g. +41761234567 or 0761234567)")
        return v

    @staticmethod
    def compute_seniority(years_experience: int) -> str:
        """
        Map years_experience -> seniority label
        """
        if years_experience < 3:
            return 'junior'
        if years_experience < 7:
            return 'mid'
        if years_experience < 12:
            return 'senior'
        return 'lead'

    @validator('seniority', always=True, pre=True)
    def set_or_validate_seniority(cls, v, values):
        # If a seniority value is provided, keep it; otherwise compute from years_experience
        if v:
            return v
        ye = values.get('years_experience')
        if ye is not None:
            return cls.compute_seniority(ye)
        return v

if __name__ == '__main__':
    # Export JSON schema to data/schemas/swiss_persona.schema.json
    schema_json = SwissPersona.schema_json(indent=2)
    out_path = os.path.abspath(os.path.join(os.getcwd(), 'data', 'schemas', 'swiss_persona.schema.json'))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf8') as f:
        f.write(schema_json)
    print(f"Wrote SwissPersona JSON schema to {out_path}")



