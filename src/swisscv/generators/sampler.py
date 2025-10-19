from dataclasses import dataclass, asdict
from pathlib import Path
import random, json, datetime

CURRENT_YEAR = datetime.datetime.now().year

# Fallback canton data
FALLBACK_CANTONS = [
    {"code":"ZH","name":"Zürich","population":1540000,"workforce":820000,"language_distribution":{"de":0.95,"fr":0.02,"it":0.01}},
    {"code":"BE","name":"Bern","population":1030000,"workforce":450000,"language_distribution":{"de":0.90,"fr":0.08}},
    {"code":"VD","name":"Vaud","population":800000,"workforce":380000,"language_distribution":{"fr":0.85,"de":0.10}}
]

def _load_cantons():
    p = Path.cwd() / "data" / "official" / "cantons.json"
    if p.exists():
        try:
            data = json.loads(p.read_text(encoding="utf8"))
            if isinstance(data, list) and len(data) > 0:
                return data
        except Exception:
            pass
    return FALLBACK_CANTONS

@dataclass
class SwissPersona:
    first_name: str
    last_name: str
    full_name: str
    canton: str
    city: str
    language: str
    birth_year: int
    age: int
    experience_years: int
    current_role: str
    industry: str
    email: str
    phone: str

    def dict(self):
        return asdict(self)

def sample_persona_seeded(seed: int = None, canton_code: str = None):
    if seed is not None:
        random.seed(int(seed))
    cantons = _load_cantons() or FALLBACK_CANTONS

    # If caller requested a canton code, try to find it
    canton_dict = None
    if canton_code:
        for c in cantons:
            if str(c.get("code")) == str(canton_code):
                canton_dict = c
                break

    # If not forced, do population/workforce-weighted sample
    if canton_dict is None:
        weights = []
        for c in cantons:
            w = c.get("workforce") or c.get("population") or 1
            weights.append(max(0, w))
        if sum(weights) == 0:
            canton_dict = random.choice(cantons)
        else:
            idx = random.choices(range(len(cantons)), weights=weights, k=1)[0]
            canton_dict = cantons[idx]

    # Ensure we have a safe dict
    if not isinstance(canton_dict, dict):
        canton_dict = FALLBACK_CANTONS[0]

    # Pick language according to canton language distribution
    lang_dist = canton_dict.get("language_distribution") or {"de": 1.0}
    # protect against malformed language dict
    if isinstance(lang_dist, dict) and len(lang_dist) > 0:
        langs, probs = zip(*[(k, float(v)) for k, v in lang_dist.items()])
    else:
        langs, probs = ("de",), (1.0,)

    try:
        language = random.choices(langs, probs, k=1)[0]
    except Exception:
        language = "de"

    # small name pools (MVP)
    first_names = {"de":["Stefan","Lukas","Anna","Sofia"], "fr":["Pierre","Claire","Sophie"], "it":["Luca","Giulia","Marco"]}
    last_names  = ["Meier","Müller","Schmid","Bianchi","Dubois","Bernard","Rossi"]

    fn = random.choice(first_names.get(language, ["Alex"]))
    ln = random.choice(last_names)

    birth_year = random.randint(CURRENT_YEAR - 60, CURRENT_YEAR - 25)
    education_exit_age = random.randint(22,26)
    age = CURRENT_YEAR - birth_year
    experience_years = max(0, age - education_exit_age)

    persona = SwissPersona(
        first_name=fn,
        last_name=ln,
        full_name=f"{fn} {ln}",
        canton=canton_dict.get("code") or "ZH",
        city=canton_dict.get("name") or "Zürich",
        language=language,
        birth_year=birth_year,
        age=age,
        experience_years=experience_years,
        current_role="Software Engineer",
        industry="technology",
        email=f"{fn.lower()}.{ln.lower()}@example.ch",
        phone="0791234567"
    )
    return persona


