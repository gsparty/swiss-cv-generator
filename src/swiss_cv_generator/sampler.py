"""
sampler.py

Population-weighted canton sampler + simple age/experience heuristics.

Behavior:
 - If data/raw/canton_population_2024.csv exists, load populations from it.
   CSV must have header: canton_code,population
 - Otherwise, use built-in fallback weights (approximate) so dev can continue.
 - Exposes:
     load_canton_populations(path=None) -> dict[canton_code] = population (int)
     sample_canton(seed=None) -> single canton code
     sample_cantons(n, seed=None) -> list of canton codes
     sample_age(seed=None) -> sample age (int), default working-age distribution (16-70)
     compute_years_experience_from_age(age, rng) -> simple heuristic

Note: Replace fallback CSV with the authoritative BFS CSV when available.
"""
from __future__ import annotations
from typing import Dict, List, Optional, Tuple
import csv
import os
import random

# Minimal fallback populations (approximate, for dev only).
# Replace these numbers with official BFS canton totals when you have the CSV.
FALLBACK_POPULATIONS = {
    "ZH": 1620000,  # Zürich
    "BE": 1100000,  # Bern
    "LU": 430000,   # Luzern
    "UR": 38000,    # Uri
    "SZ": 165000,   # Schwyz
    "OW": 38000,    # Obwalden
    "NW": 43000,    # Nidwalden
    "GL": 41000,    # Glarus
    "ZG": 145000,   # Zug
    "FR": 340000,   # Fribourg
    "SO": 270000,   # Solothurn
    "BS": 200000,   # Basel-Stadt
    "BL": 305000,   # Basel-Landschaft
    "SH": 82000,    # Schaffhausen
    "AR": 56000,    # Appenzell Ausserrhoden
    "AI": 16000,    # Appenzell Innerrhoden
    "SG": 510000,   # St. Gallen
    "GR": 200000,   # Graubünden
    "AG": 730000,   # Aargau
    "TG": 289000,   # Thurgau
    "TI": 390000,   # Ticino
    "VD": 830000,   # Vaud
    "VS": 352000,   # Valais
    "NE": 170000,   # Neuchâtel
    "GE": 530000,   # Geneva
    "JU": 73000     # Jura
}

DEFAULT_CSV_PATH = os.path.join("data", "raw", "canton_population_2024.csv")

def load_canton_populations(path: Optional[str] = None) -> Dict[str, int]:
    """
    Load canton populations from CSV (canton_code,population). If CSV
    doesn't exist, return fallback dict.
    """
    p = path or DEFAULT_CSV_PATH
    if os.path.exists(p):
        populations: Dict[str, int] = {}
        with open(p, newline='', encoding='utf-8') as fh:
            reader = csv.DictReader(fh)
            # Accept columns: canton_code,population  (case-insensitive)
            for row in reader:
                code = row.get("canton_code") or row.get("canton") or row.get("code")
                pop = row.get("population") or row.get("pop") or row.get("value")
                if code is None or pop is None:
                    continue
                try:
                    populations[code.strip()] = int(float(pop))
                except Exception:
                    continue
        if populations:
            return populations
        # fall through to fallback if CSV empty/invalid
    # fallback
    return FALLBACK_POPULATIONS.copy()

def _to_weighted_lists(populations: Dict[str, int]) -> Tuple[List[str], List[float]]:
    items = sorted(populations.items(), key=lambda x: x[0])
    codes = [c for c, _ in items]
    weights = [float(v) for _, v in items]
    # normalize weights for random.choices
    total = sum(weights)
    if total <= 0:
        # uniform fallback
        return codes, [1.0]*len(codes)
    return codes, weights

def sample_canton(seed: Optional[int] = None, path: Optional[str] = None) -> str:
    populations = load_canton_populations(path)
    codes, weights = _to_weighted_lists(populations)
    if seed is not None:
        rnd = random.Random(seed)
        return rnd.choices(codes, weights=weights, k=1)[0]
    return random.choices(codes, weights=weights, k=1)[0]

def sample_cantons(n: int = 1, seed: Optional[int] = None, path: Optional[str] = None) -> List[str]:
    populations = load_canton_populations(path)
    codes, weights = _to_weighted_lists(populations)
    rnd = random.Random(seed)
    return rnd.choices(codes, weights=weights, k=n)

def sample_age(seed: Optional[int] = None) -> int:
    """
    Sample age using a simple working-age distribution:
    - Use a triangular distribution biased to mid-30s (mode ~35)
    - Limit to [16, 70]
    """
    rnd = random.Random(seed)
    a, b, c = 16, 70, 35
    # Python's triangular expects (low, high, mode)
    age = rnd.triangular(a, b, c)
    return int(round(age))

def compute_years_experience_from_age(age: int, rng: Optional[random.Random] = None) -> int:
    """
    Heuristic: assume education until 22-25, some career breaks.
    years_experience = max(0, age - (edu_years) - random_break)
    """
    if rng is None:
        rng = random.Random()
    # typical school -> 22, some go to 25 depending on degree
    edu_start = rng.choice([22, 23, 24, 25])
    # occasional career break years
    breaks = rng.choices([0, 0, 0, 1, 2], weights=[60,20,10,6,4], k=1)[0]
    years = max(0, age - edu_start - breaks)
    return years

# quick smoke test helper
def smoke_test_sample(n: int = 1000, seed: Optional[int] = None, path: Optional[str] = None):
    rnd = random.Random(seed)
    samples = sample_cantons(n=n, seed=seed, path=path)
    counts: Dict[str,int] = {}
    for c in samples:
        counts[c] = counts.get(c,0) + 1
    # convert to percentage
    result = {k: (v / n) * 100.0 for k, v in counts.items()}
    return result

if __name__ == "__main__":
    print("Loaded populations (top 8):")
    pops = load_canton_populations()
    for i, (k,v) in enumerate(sorted(pops.items(), key=lambda x:-x[1])):
        if i >= 8:
            break
        print(f"  {k}: {v:,}")
    print("Sampling 10 cantons (seed=42):", sample_cantons(10, seed=42))



