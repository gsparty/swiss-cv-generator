import json


def export_json(persona, filepath: str):
    with open(filepath, "w", encoding="utf8") as f:
        json.dump(persona.__dict__, f, ensure_ascii=False, indent=2)

