from dataclasses import dataclass, asdict
from pathlib import Path
import random, json, datetime

CURRENT_YEAR = datetime.datetime.now().year

# Fallback canton data (used if data/official/cantons.json missing)
FALLBACK_CANTONS = [
    {"code":"ZH","name":"Zürich","population":1540000,"workforce":820000,"language_distribution":{"de":0.95,"fr":0.02,"it":0.01}},
    {"code":"BE","name":"Bern","population":1030000,"workforce":450000,"language_distribution":{"de":0.90,"fr":0.08}},
    {"code":"VD","name":"Vaud","population":800000,"workforce":380000,"language_distribution":{"fr":0.85,"de":0.10}}
]

def _load_cantons():
    p = Path.cwd() / "data" / "official" / "cantons.json"
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf8"))
        except Exception:
            return FALLBACK_CANTONS
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

    # compatibility with existing code expecting .dict()
    def dict(self):
        return asdict(self)

def sample_persona_seeded(seed: int = None, canton_code: str = None):
    if seed is not None:
        random.seed(int(seed))
    cantons = _load_cantons()
    # choose canton weighted by workforce/population
    weights = [c.get("workforce", c.get("population", 1)) for c in cantons]
    if sum(weights) == 0:
        canton = random.choice(cantons)
    else:
        canton = random.choices(cantons, weights=weights, k=1)[0]
    if canton_code:
        matches = [c for c in cantons if c.get("code") == canton_code]
        if matches:
            canton = matches[0]

    # language sampling
    lang_dist = canton.get("language_distribution", {"de":1.0})
    langs, probs = zip(*lang_dist.items())
    language = random.choices(langs, probs, k=1)[0]

    # simple name pools (MVP). Replace with real name DB later.
    first_names = {"de":["Stefan","Lukas","Anna","Sofia"], "fr":["Pierre","Claire","Sophie"], "it":["Luca","Giulia","Marco"]}
    last_names = ["Meier","Müller","Schmid","Bianchi","Dubois","Bernard","Rossi"]

    fn = random.choice(first_names.get(language, ["Alex"]))
    ln = random.choice(last_names)

    birth_year = random.randint(CURRENT_YEAR-60, CURRENT_YEAR-25)  # ages 25..60
    education_exit_age = random.randint(22,26)
    experience_years = max(0, (CURRENT_YEAR - birth_year) - education_exit_age)
    persona = SwissPersona(
        first_name=fn,
        last_name=ln,
        full_name=f"{fn} {ln}",
        canton=canton.get("code"),
        city=canton.get("name"),
        language=language,
        birth_year=birth_year,
        age=(CURRENT_YEAR - birth_year),
        experience_years=experience_years,
        current_role="Software Engineer",
        industry="technology",
        email=f"{fn.lower()}.{ln.lower()}@example.ch",
        phone="0791234567"
    )
    return persona
