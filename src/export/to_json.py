import json
from typing import Any
from src.data.models import SwissPersona

def persona_to_json(persona: SwissPersona) -> str:
    # Use Pydantic .json() if available; for portability, use dict -> json
    d = persona.dict()
    return json.dumps(d, ensure_ascii=False, indent=2)

def save_persona_json(persona: SwissPersona, path: str):
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write(persona_to_json(persona))


