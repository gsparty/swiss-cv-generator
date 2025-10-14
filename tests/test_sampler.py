from src.models.sampler import sample_canton
import json
import pytest

def test_sample_canton_determinism():
    c1 = sample_canton('data/processed/pop_by_canton.json', seed=42)
    c2 = sample_canton('data/processed/pop_by_canton.json', seed=42)
    assert c1 == c2
    # must be one of the keys in our snapshot
    with open('data/processed/pop_by_canton.json','r',encoding='utf-8') as f:
        data = json.load(f)
    assert c1 in data.keys()
