# src/generation/sampling.py
import random, os, csv
from datetime import date
from src.data.loader import load_cantons_csv, load_companies_csv, load_occupations_json
from src.data.models import SwissPersona, Language
def weighted_choice(items, weights):
    total = sum(weights); r = random.random() * total; upto = 0
    for item, w in zip(items, weights):
        if upto + w >= r: return item
        upto += w
    return items[-1]
def load_name_csv(path):
    names, weights = [], []
    if not os.path.exists(path): return names, weights
    with open(path, newline='', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        for r in reader:
            nm = r.get('name') or r.get('Name') or r.get('vorname') or next(iter(r.values()))
            freq = r.get('frequency') or r.get('freq') or r.get('anzahl') or r.get('count') or '1'
            try: w = int(freq)
            except: w = 1
            names.append(nm); weights.append(w)
    return names, weights
class SamplingEngine:
    def __init__(self, data_dir='data'):
        self.cantons = load_cantons_csv(os.path.join(data_dir,'cantons.csv'))
        self.companies = load_companies_csv(os.path.join(data_dir,'companies.csv'))
        try: self.occupations = load_occupations_json(os.path.join(data_dir,'occupations.json'))
        except: self.occupations = []
        self.surnames, self.surname_weights = load_name_csv(os.path.join(data_dir,'surnames.csv'))
        self.names_de, self.names_de_weights = load_name_csv(os.path.join(data_dir,'names_de.csv'))
        self.names_fr, self.names_fr_weights = load_name_csv(os.path.join(data_dir,'names_fr.csv'))
        self.names_it, self.names_it_weights = load_name_csv(os.path.join(data_dir,'names_it.csv'))
    def sample_canton(self):
        weights = [c.population for c in self.cantons]; return weighted_choice(self.cantons, weights)
    def sample_language_for_canton(self, canton):
        probs = {canton.primary_language: 0.9}
        for l in ['de','fr','it']:
            if l != canton.primary_language: probs[l] = probs.get(l, 0.05)
        langs = list(probs.keys()); weights = list(probs.values()); return Language(weighted_choice(langs, weights))
    def sample_age(self, min_age=20, max_age=65): return random.randint(min_age, max_age)
    def age_to_experience(self, age, education_end_age=22, variance=2.0):
        base = max(0, age - education_end_age); var = int(random.gauss(0, variance)); return max(0, base + var)
    def career_level_from_experience(self, experience, industry):
        if experience < 3: return 'Junior'
        if experience < 7: return 'Mid'
        return 'Senior'
    def sample_name(self, language, gender=None):
        surname = weighted_choice(self.surnames, self.surname_weights) if self.surnames else random.choice(['Müller','Meier','Schmid','Bianchi'])
        if language == Language.de and self.names_de: first = weighted_choice(self.names_de, self.names_de_weights)
        elif language == Language.fr and self.names_fr: first = weighted_choice(self.names_fr, self.names_fr_weights)
        elif language == Language.it and self.names_it: first = weighted_choice(self.names_it, self.names_it_weights)
        else:
            pool = (self.names_de + self.names_fr + self.names_it); w = (self.names_de_weights + self.names_fr_weights + self.names_it_weights)
            first = weighted_choice(pool, w) if pool else random.choice(['Luca','Anna','Marco','Sophie'])
        return first, surname
    def sample_persona(self, preferred_canton=None, preferred_industry=None):
        canton = None
        if preferred_canton and preferred_canton != 'all': canton = next((c for c in self.cantons if c.code == preferred_canton), None)
        if not canton: canton = self.sample_canton()
        language = self.sample_language_for_canton(canton)
        age = self.sample_age(); exp = self.age_to_experience(age)
        industry = preferred_industry or (self.occupations[0].industry if self.occupations else 'technology')
        possible_companies = [c for c in self.companies if c.industry == industry and c.canton == canton.code]
        company = possible_companies[0].name if possible_companies else (self.companies[0].name if self.companies else 'Acme AG')
        first, surname = self.sample_name(language)
        full = f"{first} {surname}"
        persona = SwissPersona(
            first_name=first,
            last_name=surname,
            full_name=full,
            canton=canton.code,
            language=language,
            age=age,
            birth_year=date.today().year - age,
            gender=random.choice(['male','female','other']),
            experience_years=exp,
            industry=industry,
            current_title=f"{self.career_level_from_experience(exp, industry)} {industry.capitalize()}",
            career_history=[{'title': f"{self.career_level_from_experience(exp, industry)} {industry}", 'company': company, 'start_date': '2018-01', 'end_date': '2022-12', 'desc': 'Worked on projects.'}],
            email=f"{first.lower()}.{surname.lower()}@example.ch",
            phone=f"07{random.randint(60,99)}{random.randint(100000,999999)}",
            skills=['Problem solving', 'Software development'],
            summary=None,
            photo_path=None
        )
        return persona
