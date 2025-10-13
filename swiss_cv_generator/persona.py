import random
from datetime import datetime
from typing import Optional

from .data_loaders import load_cantons
from .models import EducationItem, ExperienceItem, SwissPersona

COMMON_NAMES = {
    "de": {
        "male": ["Andreas", "Thomas", "Stefan"],
        "female": ["Sandra", "Claudia", "Monika"],
        "surnames": ["Müller", "Meier", "Schneider"],
    },
    "fr": {
        "male": ["Pierre", "Jean", "Marc"],
        "female": ["Marie", "Sophie", "Anne"],
        "surnames": ["Martin", "Dubois", "Bernard"],
    },
    "it": {
        "male": ["Marco", "Luca", "Stefano"],
        "female": ["Maria", "Giulia", "Laura"],
        "surnames": ["Rossi", "Bianchi", "Ferrari"],
    },
}

MOBILE_PREFIXES = ["076", "077", "078", "079"]


def sample_canton(cantons=None) -> str:
    cantons = cantons or load_cantons()
    keys = list(cantons.keys())
    weights = [cantons[k].get("weight", 1.0) for k in keys]
    return random.choices(keys, weights=weights, k=1)[0]


def build_persona(
    age: Optional[int] = None, language: Optional[str] = None
) -> SwissPersona:
    cantons = load_cantons()
    canton_key = sample_canton(cantons)
    canton = cantons[canton_key]
    lang = language or canton.get("language", "de")
    gender = random.choice(["male", "female"])

    first = random.choice(COMMON_NAMES[lang][gender])
    last = random.choice(COMMON_NAMES[lang]["surnames"])
    name = f"{first} {last}"

    age = age or random.randint(23, 50)
    years_experience = max(0, age - 22)

    # title mapping based on experience
    if years_experience >= 10:
        title = "Senior " + random.choice(["Developer", "Engineer", "Analyst"])
    elif years_experience >= 4:
        title = random.choice(["Developer", "Engineer", "Analyst"])
    else:
        title = "Junior " + random.choice(["Developer", "Engineer", "Analyst"])

    phone = f"+41 {random.choice(MOBILE_PREFIXES)} {random.randint(1000000,9999999)}"
    email = f"{first.lower()}.{last.lower()}@gmx.ch"

    current_year = datetime.now().year
    exp = [
        ExperienceItem(
            role=title,
            company="Beispiel AG",
            from_year=current_year - 2,
            to_year=current_year,
        )
    ]
    edu = [
        EducationItem(
            degree="Bachelor Informatik", institution="ZHAW", year=current_year - 6
        )
    ]

    persona = SwissPersona(
        name=name,
        age=age,
        gender=gender,
        canton=canton_key,
        city=canton.get("name"),
        language=lang,
        title=title,
        years_experience=years_experience,
        email=email,
        phone=phone,
        experience=exp,
        education=edu,
        skills=["Python", "Datenanalyse", "Kommunikation"],
    )
    return persona
