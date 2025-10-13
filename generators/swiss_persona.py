from dataclasses import dataclass, field
from typing import Dict, Optional

from data_loaders.swiss_data_loader import SwissDataLoader

@dataclass
class SwissPersona:
    first_name: str
    last_name: str
    age: int
    gender: str
    nationality: str

    canton: dict
    city: str

    occupation: dict
    years_experience: int

    email: str
    phone: str
    linkedin_url: str

    primary_language: str
    languages: Dict[str, float] = field(default_factory=dict)
    current_employer: Optional[str] = None
