import csv
import json
from typing import List, Dict
from .models import CantonInfo, OccupationCategory, CompanyInfo
import pathlib

def load_cantons_csv(path: str) -> List[CantonInfo]:
    cants = []
    with open(path, newline='', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        for r in reader:
            # expected columns: code,name,population,workforce,primary_language
            cants.append(CantonInfo(
                code=r['code'],
                name=r['name'],
                population=int(r.get('population') or 0),
                workforce=int(r.get('workforce') or 0) if r.get('workforce') else None,
                primary_language=r.get('primary_language') or 'de'
            ))
    return cants

def load_companies_csv(path: str) -> List[CompanyInfo]:
    comps = []
    with open(path, newline='', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        for r in reader:
            comps.append(CompanyInfo(
                name=r['name'],
                canton=r.get('canton',''),
                industry=r.get('industry',''),
                size_band=r.get('size_band')
            ))
    return comps

def load_occupations_json(path: str) -> List[OccupationCategory]:
    with open(path, 'r', encoding='utf-8') as fh:
        data = json.load(fh)
    occs = [OccupationCategory(**o) for o in data.get('occupations',[])]
    return occs

# NOTE: Replace data/*.csv & data/occupations.json with official SFSO files for accuracy.
