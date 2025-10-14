import random
from dataclasses import dataclass, asdict, is_dataclass
from typing import Any, Dict, Optional, List

# try to import shared data loader helpers
try:
    from .data_loaders import load_cantons, load_occupations, load_companies, sample_weighted
except Exception:
    # fallback if import path differs
    from src.swiss_cv.data_loaders import load_cantons, load_occupations, load_companies, sample_weighted

# try to reuse existing SwissPersona dataclass if present
try:
    from .persona import SwissPersona
except Exception:
    @dataclass
    class SwissPersona:
        first_name: str
        last_name: str
        age: int
        years_experience: int
        gender: str
        primary_language: str
        canton: str
        city: str
        phone: str
        email: str
        title: str
        industry: str

def _get_field(obj: Any, keys: List[str], default=None):
    """
    Safe getter for dict-like or object-like items. Try each key in keys.
    """
    if obj is None:
        return default
    # dict-like
    try:
        for k in keys:
            if isinstance(obj, dict) and k in obj:
                return obj[k]
            if hasattr(obj, k):
                return getattr(obj, k)
    except Exception:
        pass
    # if obj itself is a string, return it for 'name'-like keys
    if isinstance(obj, str) and "name" in keys:
        return obj
    return default

def _normalize_name(s: str) -> str:
    return s.replace("ü", "ue").replace("ö", "oe").replace("ä", "ae")

def _generate_phone(rnd: random.Random) -> str:
    prefix = rnd.choice(["076","077","078","079"])
    number = "".join(str(rnd.randint(0,9)) for _ in range(7))
    return f"+41 {prefix} {number[:3]} {number[3:]}"

def _make_email(first: str, last: str, rnd: random.Random) -> str:
    domains = ["gmx.ch","bluewin.ch","sunrise.ch"]
    local = f"{first}.{last}".lower()
    local = local.replace("ü","ue").replace("ö","oe").replace("ä","ae")
    if rnd.random() < 0.25:
        local += str(rnd.randint(1,99))
    return f"{local}@{rnd.choice(domains)}"

def sensible_title_for_experience(base_title: str, years: int, rnd: random.Random) -> str:
    # Conservative mapping; prefer base_title when it exists
    if base_title:
        base = base_title
    else:
        base = "Professional"
    if years >= 12:
        return rnd.choice([f"Senior {base}", f"Lead {base}", f"Principal {base}"])
    if years >= 6:
        return rnd.choice([f"Senior {base}", f"{base}"])
    if years >= 2:
        return rnd.choice([base, f"Junior {base}"])
    return f"Junior {base}"

def generate_persona(seed: Optional[int] = None, canton: Optional[Any] = None, occupation: Optional[Any] = None, company: Optional[Any] = None) -> SwissPersona:
    """
    Robust persona generator:
      * canton / occupation / company may be None, a dict, or a string (name/code)
      * missing fields are handled gracefully
    """
    rnd = random.Random(seed)

    # Load data pools
    cantons = load_cantons()
    occupations = load_occupations()
    companies = load_companies()

    # Resolve canton object
    canton_obj = None
    if canton is None:
        canton_obj = sample_weighted(cantons, weight_key="workforce", rnd=rnd)
    elif isinstance(canton, str):
        # try to find by code or name
        canton_obj = next((c for c in cantons if str(_get_field(c, ["code","id","name"], "")).lower() == canton.lower() or str(_get_field(c, ["name","major_city"], "")).lower() == canton.lower()), None)
        if canton_obj is None:
            # fuzzy contains
            canton_obj = next((c for c in cantons if canton.lower() in str(_get_field(c, ["name","major_city"], "")).lower()), None)
        if canton_obj is None:
            canton_obj = sample_weighted(cantons, weight_key="workforce", rnd=rnd)
    else:
        canton_obj = canton

    # Resolve occupation object
    occ_obj = None
    if occupation is None:
        occ_obj = rnd.choice(occupations) if occupations else {"title":"Professional","industry":"General"}
    elif isinstance(occupation, str):
        occ_obj = next((o for o in occupations if str(_get_field(o, ["title","occupation"], "")).lower() == occupation.lower()), None)
        if occ_obj is None:
            occ_obj = next((o for o in occupations if occupation.lower() in str(_get_field(o, ["title","occupation"], "")).lower()), None)
        if occ_obj is None:
            occ_obj = rnd.choice(occupations) if occupations else {"title":"Professional","industry":"General"}
    else:
        occ_obj = occupation

    # Resolve company object
    comp_obj = None
    if company is None:
        comp_obj = rnd.choice(companies) if companies else {"name":"Freelance","industry":_get_field(occ_obj, ["industry"], "General")}
    elif isinstance(company, str):
        comp_obj = next((c for c in companies if str(_get_field(c, ["name","company","id"], "")).lower() == company.lower()), None)
        if comp_obj is None:
            comp_obj = next((c for c in companies if company.lower() in str(_get_field(c, ["name","company"], "")).lower()), None)
        if comp_obj is None:
            comp_obj = rnd.choice(companies) if companies else {"name":"Freelance","industry":_get_field(occ_obj, ["industry"], "General")}
    else:
        comp_obj = company

    # language and city/canton strings
    language = _get_field(canton_obj, ["language"], "de")
    canton_name = _get_field(canton_obj, ["name","code","id"], "Unknown")
    city = _get_field(canton_obj, ["major_city","city"], "")

    # age & experience
    age = rnd.randint(22, 60)
    years = max(0, age - 22)

    # name pools (extend these JSON-driven lists later)
    names = {
        "de": {"first":["Andreas","Sandra","Michael","Claudia","Stefan"], "last":["Müller","Meier","Keller","Schneider"]},
        "fr": {"first":["Pierre","Marie","Luc","Sophie"], "last":["Martin","Dubois","Bernard"]},
        "it": {"first":["Marco","Maria","Luca","Giulia"], "last":["Rossi","Bianchi","Fontana"]}
    }
    pool = names.get(language, names["de"])
    first = rnd.choice(pool["first"])
    last = rnd.choice(pool["last"])

    phone = _generate_phone(rnd)
    email = _make_email(first, last, rnd)
    base_title = _get_field(occ_obj, ["title","occupation"], "Professional")
    title = sensible_title_for_experience(base_title, years, rnd)
    industry = _get_field(occ_obj, ["industry"], _get_field(comp_obj, ["industry"], "General"))

    persona = SwissPersona(
        first_name=first,
        last_name=last,
        age=age,
        years_experience=years,
        gender="unspecified",
        primary_language=language,
        canton=canton_name,
        city=city,
        phone=phone,
        email=email,
        title=title,
        industry=industry
    )
    return persona
