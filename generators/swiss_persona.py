# generators/persona.py
import random
from dataclasses import asdict, dataclass


@dataclass
class SwissPersona:
    first_name: str
    last_name: str
    age: int
    years_experience: int
    gender: str
    primary_language: str  # 'de'|'fr'|'it'
    canton: str
    city: str
    phone: str
    email: str
    title: str
    industry: str


def years_from_age(age: int) -> int:
    return max(0, age - 22)


def generate_persona(data, *, seed=None):
    rnd = random.Random(seed)
    canton = sample_canton(data["cantons"], rnd)
    primary_language = canton["language"]
    age = rnd.randint(22, 60)
    years = years_from_age(age)
    # pick name pools per language (load from data)
    name_pool = data["names"][primary_language]
    first_name = rnd.choice(name_pool["first"])
    last_name = rnd.choice(name_pool["last"])
    phone = generate_phone(primary_language, rnd)
    email = make_email(first_name, last_name, rnd)
    title = sample_title(years, data["titles"], rnd)
    return SwissPersona(
        first_name,
        last_name,
        age,
        years,
        "unspecified",
        primary_language,
        canton["name"],
        canton.get("major_city", ""),
        phone,
        email,
        title,
        rnd.choice(data["industries"]),
    )
