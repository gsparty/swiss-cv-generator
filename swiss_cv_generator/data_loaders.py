import json
from pathlib import Path
from typing import Dict, Any

DATA_DIR = Path(__file__).parent.parent / "data"


def load_cantons(path: Path | None = None) -> Dict[str, Any]:
    """
    Load cantons JSON file. Handles files with a UTF-8 BOM by opening with 'utf-8-sig'.
    If the file is missing or invalid, return a small built-in fallback dataset.
    """
    p = path or DATA_DIR / "cantons.json"
    if not p.exists():
        # fallback minimal data if none provided
        return {
            "ZH": {"name": "Zürich", "language": "de", "weight": 1.0},
            "BE": {"name": "Bern", "language": "de", "weight": 0.6},
            "GE": {"name": "Genf", "language": "fr", "weight": 0.4},
            "TI": {"name": "Ticino", "language": "it", "weight": 0.15},
        }

    try:
        # open with utf-8-sig to silently strip a UTF-8 BOM if present
        with p.open("r", encoding="utf-8-sig") as fh:
            return json.load(fh)
    except Exception as e:
        # If parsing fails, warn and return fallback
        print(f"Warning: failed to load cantons JSON ({p}). Using fallback dataset. Error: {e}")
        return {
            "ZH": {"name": "Zürich", "language": "de", "weight": 1.0},
            "BE": {"name": "Bern", "language": "de", "weight": 0.6},
            "GE": {"name": "Genf", "language": "fr", "weight": 0.4},
            "TI": {"name": "Ticino", "language": "it", "weight": 0.15},
        }
