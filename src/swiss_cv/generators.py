import random
from dataclasses import dataclass, asdict, is_dataclass, fields as dataclass_fields
from typing import Any, Dict, Optional, List
import inspect

# try to import shared data loader helpers
try:
    from .data_loaders import load_cantons, load_occupations, load_companies, sample_weighted
except Exception:
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
    if obj is None:
        return default
    try:
        for k in keys:
            if isinstance(obj, dict) and k in obj:
                return obj[k]
            if hasattr(obj, k):
                return getattr(obj, k)
    except Exception:
        pass
    if isinstance(obj, str) and "name" in keys:
        return obj
    return default

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
    base = base_title or "Professional"
    if years >= 12:
        return rnd.choice([f"Senior {base}", f"Lead {base}", f"Principal {base}"])
    if years >= 6:
        return rnd.choice([f"Senior {base}", f"{base}"])
    if years >= 2:
        return rnd.choice([base, f"Junior {base}"])
    return f"Junior {base}"

def _instantiate_persona_class(clazz, persona_dict: Dict[str, Any]):
    """
    Instantiate the project's persona class by selecting only supported constructor/field names.
    Works with dataclasses, pydantic-like models (try signature), or plain classes.
    Falls back to attempting to set attributes after construction if needed.
    """
    # 1) If dataclass: use dataclass field names
    try:
        if is_dataclass(clazz):
            field_names = [f.name for f in dataclass_fields(clazz)]
            kwargs = {k: persona_dict[k] for k in field_names if k in persona_dict}
            return clazz(**kwargs)
    except Exception:
        pass

    # 2) Try to use __init__ signature
    try:
        sig = inspect.signature(clazz)
        params = [
            name for name, p in sig.parameters.items()
            if name != "self" and p.kind in (inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.KEYWORD_ONLY)
        ]
        kwargs = {}
        for p in params:
            if p in persona_dict:
                kwargs[p] = persona_dict[p]
            else:
                # try common synonyms
                if p == "language" and "primary_language" in persona_dict:
                    kwargs[p] = persona_dict["primary_language"]
                elif p == "primary_language" and "language" in persona_dict:
                    kwargs[p] = persona_dict["language"]
                elif p == "years" and "years_experience" in persona_dict:
                    kwargs[p] = persona_dict["years_experience"]
                elif p == "first" and "first_name" in persona_dict:
                    kwargs[p] = persona_dict["first_name"]
                elif p == "last" and "last_name" in persona_dict:
                    kwargs[p] = persona_dict["last_name"]
        return clazz(**kwargs)
    except Exception:
        pass

    # 3) Try to instantiate with no args and set attributes
    try:
        inst = clazz()
        for k, v in persona_dict.items():
            try:
                setattr(inst, k, v)
            except Exception:
                pass
        return inst
    except Exception:
        pass

    # 4) Final fallback: return the persona_dict itself
    return persona_dict

def generate_persona(seed: Optional[int] = None, canton: Optional[Any] = None, occupation: Optional[Any] = None, company: Optional[Any] = None):
    rnd = random.Random(seed)

    cantons = load_cantons()
    occupations = load_occupations()
    companies = load_companies()

    # Resolve canton
    if canton is None:
        canton_obj = sample_weighted(cantons, weight_key="workforce", rnd=rnd)
    elif isinstance(canton, str):
        canton_obj = next((c for c in cantons if str(_get_field(c, ["code","id","name"], "")).lower() == canton.lower() or str(_get_field(c, ["name","major_city"], "")).lower() == canton.lower()), None)
        if canton_obj is None:
            canton_obj = next((c for c in cantons if canton.lower() in str(_get_field(c, ["name","major_city"], "")).lower()), None)
        if canton_obj is None:
            canton_obj = sample_weighted(cantons, weight_key="workforce", rnd=rnd)
    else:
        canton_obj = canton

    # Resolve occupation
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

    # Resolve company
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

    language = _get_field(canton_obj, ["language"], "de")
    canton_name = _get_field(canton_obj, ["name","code","id"], "Unknown")
    city = _get_field(canton_obj, ["major_city","city"], "")

    age = rnd.randint(22, 60)
    years = max(0, age - 22)

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

    # Build a full persona dict
    persona_dict = {
        "first_name": first,
        "last_name": last,
        "age": age,
        "years_experience": years,
        "gender": "unspecified",
        "primary_language": language,
        "language": language,
        "canton": canton_name,
        "canton_id": _get_field(canton_obj, ["id","code"], None),
        "city": city,
        "phone": phone,
        "email": email,
        "title": title,
        "industry": industry
    }

    # Instantiate project persona class in a tolerant way
    try:
        instance = _instantiate_persona_class(SwissPersona, persona_dict)
        return instance
    except Exception:
        # final fallback: return persona_dict
        return persona_dict
