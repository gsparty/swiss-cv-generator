from pydantic import BaseModel
from typing import List, Optional


class ExperienceItem(BaseModel):
    role: str
    company: str
    from_year: int
    to_year: int


class EducationItem(BaseModel):
    degree: str
    institution: str
    year: int


class SwissPersona(BaseModel):
    name: str
    age: int
    gender: str
    canton: str
    city: Optional[str]
    language: str
    title: str
    years_experience: int
    email: str
    phone: str
    experience: List[ExperienceItem] = []
    education: List[EducationItem] = []
    skills: List[str] = []
