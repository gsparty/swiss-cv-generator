from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from enum import Enum

class Language(str, Enum):
    de = 'de'
    fr = 'fr'
    it = 'it'
    en = 'en'

class CantonInfo(BaseModel):
    code: str = Field(..., description='Canton code, e.g. ZH')
    name: str
    population: int
    workforce: Optional[int] = None
    primary_language: Language

class OccupationCategory(BaseModel):
    code: str
    title: dict  # translations: {'de': '...', 'fr': '...', 'it': '...'}
    industry: str

class CompanyInfo(BaseModel):
    name: str
    canton: str
    industry: str
    size_band: Optional[str] = None  # e.g. '1-10','11-50','50-250','250+'

class SwissPersona(BaseModel):
    first_name: str
    last_name: str
    full_name: str
    canton: str
    language: Language
    age: int
    birth_year: int
    gender: Optional[str]
    experience_years: float
    industry: str
    current_title: str
    career_history: List[dict]  # list of {'title','company','start_date','end_date','desc'}
    email: EmailStr
    phone: str
    skills: List[str]
    summary: Optional[str] = None
    photo_path: Optional[str] = None


