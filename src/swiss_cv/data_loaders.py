import json
import os
import random

HERE = os.path.dirname(__file__)


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_cantons(data_dir=None):
    if data_dir is None:
        data_dir = os.path.join(HERE, "..", "data")
    return load_json(os.path.join(data_dir, "cantons.json"))


def load_occupations(data_dir=None):
    if data_dir is None:
        data_dir = os.path.join(HERE, "..", "data")
    return load_json(os.path.join(data_dir, "occupations.json"))


def load_companies(data_dir=None):
    if data_dir is None:
        data_dir = os.path.join(HERE, "..", "data")
    return load_json(os.path.join(data_dir, "companies.json"))


def sample_weighted(items, weight_key="workforce"):
    total = sum(item.get(weight_key, 1) for item in items)
    if total <= 0:
        return random.choice(items)
    choice = random.random() * total
    upto = 0
    for it in items:
        w = it.get(weight_key, 1)
        if upto + w >= choice:
            return it
        upto += w
    return items[-1]
