import random
import math
from typing import List, Optional
from datetime import date
from src.data.loader import load_cantons_csv, load_companies_csv, load_occupations_json
from src.data.models import CantonInfo, SwissPersona, Language

def weighted_choice(items, weights):
    total = sum(weights)
    r = random.random() * total
    upto = 0
    for item, w in zip(items, weights):
        if upto + w >= r:
            return item
        upto += w
    return items[-1]

class SamplingEngine:
    def __init__(self, data_dir: str = 'data'):
        self.cantons = load_cantons_csv(f'{data_dir}/cantons.csv')
        self.companies = load_companies_csv(f'{data_dir}/companies.csv')
        self.occupations = load_occupations_json(f'{data_dir}/occupations.json')

    def sample_canton(self) -> CantonInfo:
        weights = [c.population for c in self.cantons]
        return weighted_choice(self.cantons, weights)

    def sample_language_for_canton(self, canton: CantonInfo) -> Language:
        # Primary language from canton is default; small chance of other languages
        probs = {canton.primary_language: 0.9}
        for l in ['de','fr','it']:
            if l != canton.primary_language:
                probs[l] = 0.05
        # convert to weighted list
        langs = list(probs.keys())
        weights = list(probs.values())
        return Language(weighted_choice(langs, weights))

    def sample_age(self, min_age:int=20, max_age:int=65) -> int:
        # Use skewed adult distribution: younger adults more common - simple default
        return random.randint(min_age, max_age)

    def age_to_experience(self, age:int, education_end_age:int=22, variance:float=2.0) -> int:
        base = max(0, age - education_end_age)
        # apply a normal-ish variance
        var = int(random.gauss(0, variance))
        exp = max(0, base + var)
        return exp

    def career_level_from_experience(self, experience:int, industry:str) -> str:
        # industry-specific thresholds could be loaded from a config; this is a default
        if experience < 3:
            return 'Junior'
        if experience < 7:
            return 'Mid'
        return 'Senior'

    def sample_persona(self, preferred_canton:Optional[str]=None, preferred_industry:Optional[str]=None) -> SwissPersona:
        canton = None
        if preferred_canton and preferred_canton != 'all':
            canton = next((c for c in self.cantons if c.code == preferred_canton), None)
        if not canton:
            canton = self.sample_canton()
        language = self.sample_language_for_canton(canton)
        age = self.sample_age()
        exp = self.age_to_experience(age)
        # pick industry
        industry = preferred_industry or random.choice([o['industry'] for o in self.occupations])
        # pick a company in that industry & canton if possible
        possible_companies = [c for c in self.companies if c.industry == industry and c.canton == canton.code]
        company = random.choice(possible_companies).name if possible_companies else random.choice(self.companies).name
        # Minimal persona (names & contact created later)
        persona = SwissPersona(
            first_name='Max', last_name='Mustermann',
            full_name='Max Mustermann',
            canton=canton.code,
            language=language,
            age=age,
            birth_year=date.today().year - age,
            gender=random.choice(['male','female','other']),
            experience_years=exp,
            industry=industry,
            current_title=f\"{self.career_level_from_experience(exp, industry)} {industry.capitalize()}\",
            career_history=[{'title': f\"{self.career_level_from_experience(exp, industry)} {industry}\", 'company': company, 'start_date': '2018-01', 'end_date': '2022-12', 'desc': 'Worked on projects.'}],
            email=f\"example+{random.randint(1000,9999)}@example.ch\",
            phone=f\"07{random.randint(60,99)}{random.randint(100000,999999)}\",
            skills=['Problem solving', 'Software development'],
            summary=None,
            photo_path=None
        )
        return persona
