from swiss_cv.models import SwissPersona, EducationEntry, ExperienceEntry
from swiss_cv.sampler import sample_canton, sample_age, compute_years_experience_from_age
import os, json, uuid, random, datetime

CURRENT_YEAR = datetime.date.today().year

# small language mapping and sample names (expand later by ingesting BFS name lists)
LANG_BY_CANTON = {
    "VD": "fr", "GE": "fr", "NE": "fr", "FR": "fr",
    "TI": "it",
    "ZH": "de", "BE": "de", "LU": "de", "AG": "de", "SG": "de", "GR": "de",
    # other cantons default to de
}
NAMES = {
    "de": [("Max","Muster"), ("Anna","Meier"), ("Lukas","Schneider"), ("Sophie","Frey")],
    "fr": [("Mathieu","Dupont"), ("Camille","Martin"), ("Julie","Bernard"), ("Lucas","Morel")],
    "it": [("Marco","Rossi"), ("Giulia","Bianchi"), ("Luca","Ferrari"), ("Elisa","Conti")],
    "en": [("Alex","Smith"), ("Sam","Jones")]
}

def choose_name_for_lang(lang, rnd):
    pool = NAMES.get(lang, NAMES["de"])
    return rnd.choice(pool)

def format_phone(rnd):
    # Swiss mobile: +41 7x xxxxxxx -> 9 digits after country code
    prefix = rnd.choice(["76","77","78","79"])
    rest = "".join(str(rnd.randint(0,9)) for _ in range(7))
    return f"+41{prefix}{rest}"

def format_email(first, last, rnd):
    domain = rnd.choice(["example.ch","gmail.com","bluewin.ch","gmx.ch"])
    local = f"{first}.{last}".lower().replace(" ", "")
    return f"{local}@{domain}"

def make_experience_history(years_experience, current_title="Engineer"):
    # simple single current job entry (extend later)
    start_year = CURRENT_YEAR - years_experience if years_experience > 0 else CURRENT_YEAR
    exp = ExperienceEntry(
        title=current_title,
        company="ACME AG",
        canton=None,
        start_year=start_year,
        end_year=None,
        description="Worked on projects and delivered value.",
        seniority=None
    )
    return [exp]

def generate_persona(seed=None):
    rnd = random.Random(seed)
    canton = sample_canton(seed=rnd.randint(0, 2**31-1))
    lang = LANG_BY_CANTON.get(canton, "de")
    first, last = choose_name_for_lang(lang, rnd)
    age = sample_age(seed=rnd.randint(0,2**31-1))
    years_experience = compute_years_experience_from_age(age, rng=rnd)
    # ensure validator constraints (age>=16)
    persona = SwissPersona(
        id=str(uuid.uuid4()),
        first_name=first,
        last_name=last,
        gender=rnd.choice(["male","female","other"]),
        canton=canton,
        language=lang,
        age=age,
        years_experience=years_experience,
        industry=rnd.choice(["technology","finance","healthcare","manufacturing"]),
        current_title=rnd.choice(["Software Engineer","Data Analyst","Project Manager","Consultant"]),
        email=format_email(first, last, rnd),
        phone=format_phone(rnd),
        address=None,
        skills=["communication","problem solving"],
        languages_spoken=[lang],
        education=[EducationEntry(institution="University", degree="BSc", field="Computer Science", start_year=age-22-3, end_year=age-22)],
        experience=make_experience_history(years_experience, current_title=rnd.choice(["Software Engineer","Analyst","Manager"])),
        summary=f"{first} {last} is a {years_experience}-year experienced professional in {rnd.choice(['software','data','project management'])}."
    )
    return persona

def generate(count=5, seed=42, out_dir="out_personas"):
    rnd = random.Random(seed)
    os.makedirs(out_dir, exist_ok=True)
    created = []
    for i in range(count):
        p = generate_persona(seed=rnd.randint(0,2**31-1))
        out_path = os.path.join(out_dir, f"persona_{i+1}_{p.id[:8]}.json")
        with open(out_path, "w", encoding="utf8") as f:
            f.write(p.json(indent=2, ensure_ascii=False))
        created.append(out_path)
    print(f"Generated {len(created)} personas -> {out_dir}")
    for p in created:
        print(" -", p)

if __name__ == "__main__":
    # quick default run: generate 5 personas
    generate(count=5, seed=123, out_dir="out_personas")
