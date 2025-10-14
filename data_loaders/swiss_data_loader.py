import json
import random
from pathlib import Path
from typing import Optional


class SwissDataLoader:
    def __init__(self, data_mode: str = "mock"):
        self.data_mode = data_mode
        self.base_path = Path(__file__).parent
        self._cantons = None
        self._occupations = None
        self._companies = None

    def _load(self, filename: str):
        path = self.base_path / filename
        with open(path, "r", encoding="utf8") as f:
            return json.load(f)

    @property
    def cantons(self) -> list[dict]:
        if self._cantons is None:
            self._cantons = self._load("swiss_cantons.json")
        return self._cantons

    @property
    def occupations(self) -> list[dict]:
        if self._occupations is None:
            self._occupations = self._load("swiss_occupations.json")
        return self._occupations

    @property
    def companies(self) -> list[dict]:
        if self._companies is None:
            self._companies = self._load("swiss_companies.json")
        return self._companies

    def sample_canton(self, weights_by_population: bool = True) -> dict:
        choices = self.cantons
        if weights_by_population:
            weights = [c.get("population", 1) for c in choices]
            return random.choices(choices, weights=weights, k=1)[0]
        return random.choice(choices)

    def sample_occupation(self, industry_filter: Optional[str] = None) -> dict:
        occs = self.occupations
        if industry_filter:
            occs = [o for o in occs if o.get("industry") == industry_filter]
        return random.choice(occs)

    def sample_company(self, canton_code: str) -> dict:
        comps = [c for c in self.companies if c.get("associated_canton") == canton_code]
        return random.choice(comps) if comps else random.choice(self.companies)
