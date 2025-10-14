import json
import csv
from pathlib import Path
from typing import Dict

def load_processed_population(processed_path: str = "data/processed/pop_by_canton.json") -> Dict[str, int]:
    """Load processed population by canton. If JSON missing, try CSV at data/raw/pop_by_canton.csv (simple format).
       Returns dict of canton -> count.
    """
    p = Path(processed_path)
    if p.exists():
        # use utf-8-sig to tolerate files with a BOM
        with p.open("r", encoding="utf-8-sig") as f:
            return json.load(f)
    # fallback: try CSV file in data/raw (expected two columns: canton,count)
    csv_path = Path("data/raw/pop_by_canton.csv")
    if csv_path.exists():
        out = {}
        with csv_path.open("r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if not row:
                    continue
                canton = row[0].strip()
                try:
                    count = int(float(row[1]))
                except Exception:
                    continue
                out[canton] = int(count)
        if out:
            # persist normalized processed file for deterministic tests
            p.parent.mkdir(parents=True, exist_ok=True)
            with p.open("w", encoding="utf-8") as f:
                json.dump(out, f, ensure_ascii=False, indent=2)
            return out
    raise FileNotFoundError(f"Processed population not found at {processed_path} and no CSV fallback present.")
