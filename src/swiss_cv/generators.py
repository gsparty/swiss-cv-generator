import random
from dataclasses import dataclass, is_dataclass, fields as dataclass_fields
from typing import Any, Dict, Optional, List
import inspect, types

# --- Data loader imports ---
try:
    from .data_loaders import load_cantons, load_occupations, load_companies, sample_weighted
except Exception:
    from src.swiss_cv.data_loaders import load_cantons, load_occupations, load_companies, sample_weighted

# --- Try import of SwissPersona ---
try:
    from .persona import SwissPersona
except Exception:
    SwissPersona = None  # will handle dynamically below

# --- Safe attribute access for any type ---
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

# --- Helper utilities ---
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

# --- Resilient class instantiator ---
def _instantiate_persona_class(clazz, persona_dict: Dict[str, Any]):
    try:
        if clazz and is_dataclass(clazz):
            names = [f.name for f in dataclass_fields(clazz)]
            kwargs = {k: persona_dict[k] for k in names if k in persona_dict}
            return clazz(**kwargs)
    except Exception:
        pass

    try:
        if clazz:
            sig = inspect.signature(clazz)
            valid_keys = [k for k in persona_dict if k in sig.parameters]
            kwargs = {k: persona_dict[k] for k in valid_keys}
            return clazz(**kwargs)
    except Exception:
        pass

    # fallback ? wrap as dynamic object with attributes
    obj = types.SimpleNamespace(**persona_dict)
    return obj

# --- Main persona generator ---
def generate_persona(seed: Optional[int] = None, canton: Optional[Any] = None,
                     occupation: Optional[Any] = None, company: Optional[Any] = None):
    rnd = random.Random(seed)

    cantons = load_cantons()
    occupations = load_occupations()
    companies = load_companies()

    # Resolve canton
    if canton is None:
        canton_obj = sample_weighted(cantons, weight_key="workforce", rnd=rnd)
    elif isinstance(canton, str):
        canton_obj = next((c for c in cantons if str(_get_field(c, ["code","id","name"], "")).lower() == canton.lower() or str(_get_field(c, ["name","major_city"], "")).lower() == canton.lower()), None)
        canton_obj = canton_obj or next((c for c in cantons if canton.lower() in str(_get_field(c, ["name","major_city"], "")).lower()), None)
        canton_obj = canton_obj or sample_weighted(cantons, weight_key="workforce", rnd=rnd)
    else:
        canton_obj = canton

    # Resolve occupation
    if occupation is None:
        occ_obj = rnd.choice(occupations) if occupations else {"title":"Professional","industry":"General"}
    elif isinstance(occupation, str):
        occ_obj = next((o for o in occupations if str(_get_field(o, ["title","occupation"], "")).lower() == occupation.lower()), None)
        occ_obj = occ_obj or next((o for o in occupations if occupation.lower() in str(_get_field(o, ["title","occupation"], "")).lower()), None)
        occ_obj = occ_obj or rnd.choice(occupations) if occupations else {"title":"Professional","industry":"General"}
    else:
        occ_obj = occupation

    # Resolve company
    if company is None:
        comp_obj = rnd.choice(companies) if companies else {"name":"Freelance","industry":_get_field(occ_obj, ["industry"], "General")}
    elif isinstance(company, str):
        comp_obj = next((c for c in companies if str(_get_field(c, ["name","company","id"], "")).lower() == company.lower()), None)
        comp_obj = comp_obj or next((c for c in companies if company.lower() in str(_get_field(c, ["name","company"], "")).lower()), None)
        comp_obj = comp_obj or rnd.choice(companies) if companies else {"name":"Freelance","industry":_get_field(occ_obj, ["industry"], "General")}
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

    persona_dict = dict(
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

    clazz = SwissPersona or None
    return _instantiate_persona_class(clazz, persona_dict)

# ---- Added helper: make persona JSON-serializable without changing existing API ----
def to_builtin(o):
    """
    Recursively convert SimpleNamespace/dict/list into builtin types for JSON serialization.
    Safe helper — does not mutate the originals.
    """
    from types import SimpleNamespace
    if isinstance(o, SimpleNamespace):
        return {k: to_builtin(v) for k, v in vars(o).items()}
    if isinstance(o, dict):
        return {k: to_builtin(v) for k, v in o.items()}
    if isinstance(o, list):
        return [to_builtin(i) for i in o]
    return o

def generate_persona_jsonable(*args, **kwargs):
    """
    Wrapper: call generate_persona and convert result to plain Python builtins
    so callers can JSON-dump it directly.
    """
    # import locally to avoid circular/top-level import surprises
    try:
        gen = globals().get('generate_persona')
        if gen is None:
            # fallback: try importing
            from src.swiss_cv.generators import generate_persona as gen
    except Exception:
        # if something odd, raise normally
        raise
    persona = gen(*args, **kwargs)
    return to_builtin(persona)
# ---- end added helper ----



