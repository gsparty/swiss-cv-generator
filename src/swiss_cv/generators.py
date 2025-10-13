import os
import random

from .persona import SwissPersona

# name pools (small; expand later for realism)
NAME_POOLS = {
    "de": {
        "male": ["Andreas", "Lukas", "Thomas", "Markus"],
        "female": ["Sandra", "Anna", "Monika", "Laura"],
        "last": ["Müller", "Meier", "Schmid", "Keller"],
    },
    "fr": {
        "male": ["Pierre", "Jean", "Marc", "Luc"],
        "female": ["Marie", "Camille", "Sophie", "Claire"],
        "last": ["Martin", "Dubois", "Morel", "Leroy"],
    },
    "it": {
        "male": ["Marco", "Luca", "Giovanni", "Stefano"],
        "female": ["Maria", "Elena", "Lucia", "Francesca"],
        "last": ["Rossi", "Bianchi", "Ferrari", "Galli"],
    },
}

PHONE_PREFIXES = {"default": ["076", "077", "078", "079"]}

EMAIL_DOMAINS = ["gmx.ch", "bluewin.ch", "sunrise.ch", "gmail.com"]


def years_experience_from_age(age: int):
    return max(0, age - 22)


def choose_name(language, gender):
    pool = NAME_POOLS.get(language, NAME_POOLS["de"])
    first = random.choice(pool["male"] if gender == "male" else pool["female"])
    last = random.choice(pool["last"])
    return first, last


def generate_phone():
    pref = random.choice(PHONE_PREFIXES["default"])
    rest = "".join(str(random.randint(0, 9)) for _ in range(7))
    return f"+41 {pref} {rest}"


def generate_email(first, last):
    dom = random.choice(EMAIL_DOMAINS)
    local = f"{first.lower()}.{last.lower()}"
    # replace German special chars
    local = (
        local.replace("ä", "ae")
        .replace("ö", "oe")
        .replace("ü", "ue")
        .replace("ß", "ss")
        .replace("ü", "ue")
    )
    return f"{local}@{dom}"


def sensible_title_for_experience(occupation_title, years_exp):
    # Keep the occupation title; optionally append level if experience high
    if years_exp >= 10:
        return f"Senior {occupation_title}"
    if years_exp >= 5:
        return f"{occupation_title}"
    return f"{occupation_title}"


def generate_persona(
    canton, occupation, company=None, language=None, gender=None, age=None
):
    # canton: dict with id,name,language
    lang = language or canton.get("language", "de")
    gender = gender or ("male" if random.random() < 0.5 else "female")
    if age is None:
        # age distribution (22-65); biased to working-age cluster
        age = int(random.gauss(35, 8))
        age = max(22, min(65, age))
    years = years_experience_from_age(age)
    # restrict unrealistic senior titles when experience is low by adjusting title elsewhere
    first, last = choose_name(lang, gender)
    occupation_title = sensible_title_for_experience(occupation["title"], years)
    email = generate_email(first, last)
    phone = generate_phone()
    summary = f"{first} {last} is a {occupation_title} from {canton['name']} with {years} years of experience in {occupation.get('industry','general')}."
    return SwissPersona(
        first_name=first,
        last_name=last,
        gender=gender,
        age=age,
        years_experience=years,
        canton=canton["id"],
        canton_name=canton["name"],
        language=lang,
        occupation=occupation_title,
        employer=(company["name"] if company else None),
        email=email,
        phone=phone,
        summary=summary,
    )
