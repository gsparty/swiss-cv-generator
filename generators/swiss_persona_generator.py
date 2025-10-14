import random

from data_loaders.swiss_data_loader import SwissDataLoader

from .swiss_persona import SwissPersona


class SwissPersonaGenerator:
    def __init__(self, canton_filter=None, language_filter=None, industry_filter=None):
        self.loader = SwissDataLoader()
        self.canton_filter = canton_filter
        self.language_filter = language_filter
        self.industry_filter = industry_filter

    def generate(self) -> SwissPersona:
        # 1. Sample canton
        canton = self.loader.sample_canton()
        # 2. Sample occupation
        occupation = self.loader.sample_occupation(self.industry_filter)
        # 3. Demographics
        age = random.randint(18, 65)
        years_exp = max(0, age - 22)
        gender = random.choice(["Male", "Female", "Other"])
        # 4. Names by primary language
        pl = canton.get("primary_language", "de")
        if pl == "de":
            first = random.choice(["Hans", "Julia"])
            last = random.choice(["Müller", "Meier"])
        elif pl == "fr":
            first = random.choice(["Jean", "Marie"])
            last = random.choice(["Dubois", "Moreau"])
        else:
            first = random.choice(["Luca", "Sofia"])
            last = random.choice(["Rossi", "Bianchi"])
        # 5. Contact info
        email = f"{first.lower()}.{last.lower()}@example.ch"
        phone = f"+41{random.randint(700000000,799999999)}"
        linkedin = f"https://www.linkedin.com/in/{first.lower()}{last.lower()}"
        # 6. Employer
        company = self.loader.sample_company(canton["code"])
        # 7. Languages
        languages = {pl: 1.0}

        return SwissPersona(
            first_name=first,
            last_name=last,
            age=age,
            gender=gender,
            nationality="Swiss",
            canton=canton,
            city=random.choice(canton.get("major_cities", [""])),
            occupation=occupation,
            years_experience=years_exp,
            email=email,
            phone=phone,
            linkedin_url=linkedin,
            primary_language=pl,
            languages=languages,
            current_employer=company.get("name", ""),
        )
