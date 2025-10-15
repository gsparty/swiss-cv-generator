import json, random, os

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "pop_by_canton.json")
with open(DATA_PATH, encoding="utf8") as f:
    DATA = json.load(f)

_cantons = [d["canton"] for d in DATA]
_weights = [d["population"] for d in DATA]

def sample_canton_language():
    canton = random.choices(_cantons, weights=_weights, k=1)[0]
    lang_map = {"ZH":"de","BE":"de","VD":"fr","GE":"fr","TI":"it"}
    language = lang_map.get(canton, "de")
    return canton, language

# Quick smoke test
from collections import Counter
c = Counter(sample_canton_language()[0] for _ in range(1000))
print("Sample canton frequencies (1000 draws):")
for k,v in c.most_common(10):
    print(f"{k}: {v}")
