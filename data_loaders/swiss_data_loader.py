import json
from pathlib import Path

class SwissDataLoader:
    def __init__(self, data_mode: str = 'mock'):
        self.data_mode = data_mode
        self.base_path = Path(__file__).parent
        self._cantons = None
        self._occupations = None
        self._companies = None

    def _load(self, filename):
        path = self.base_path / filename
        with open(path, 'r', encoding='utf8') as f:
            return json.load(f)

    @property
    def cantons(self):
        if self._cantons is None:
            self._cantons = self._load('swiss_cantons.json')
        return self._cantons

    @property
    def occupations(self):
        if self._occupations is None:
            self._occupations = self._load('swiss_occupations.json')
        return self._occupations

    @property
    def companies(self):
        if self._companies is None:
            self._companies = self._load('swiss_companies.json')
        return self._companies

    # TODO: Implement sample_canton, sample_occupation, sample_company
