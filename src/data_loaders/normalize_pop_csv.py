import csv
import json
from pathlib import Path
from typing import Dict, Optional

# This utility expects a CSV with either:
#  - headers: 'canton' and 'population' (case-insensitive), or
#  - two columns: canton_code,population
#
# It writes a JSON mapping canton_code -> population to data/processed/pop_by_canton.json

COMMON_HEADERS = ['canton','kanton','code','canton_code']
POP_HEADERS = ['population','pop','count','inhabitants','people']

def _find_column_index(headers, candidates):
    low = [h.lower() for h in headers]
    for c in candidates:
        if c.lower() in low:
            return low.index(c.lower())
    return None

def normalize_population_csv(csv_path: str = 'data/raw/pop_by_canton.csv', out_json: str = 'data/processed/pop_by_canton.json') -> Dict[str,int]:
    p = Path(csv_path)
    if not p.exists():
        raise FileNotFoundError(f'CSV input not found: {csv_path}')
    with p.open('r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
    if not rows:
        raise ValueError('CSV file is empty')

    headers = [h.strip() for h in rows[0]]
    # detect header vs no-header
    has_header = False
    if any(h for h in headers if h):
        # simple heuristic: if first row contains non-numeric in first column -> header
        if not headers[0].strip().replace('"','').isdigit():
            has_header = True

    data = {}
    if has_header:
        # find column indices
        canton_idx = _find_column_index(headers, COMMON_HEADERS) or 0
        pop_idx = _find_column_index(headers, POP_HEADERS) or (1 if len(headers) > 1 else None)
        if pop_idx is None:
            raise ValueError('Could not detect population column in CSV header.')
        for row in rows[1:]:
            if not row:
                continue
            canton = row[canton_idx].strip()
            pop_raw = row[pop_idx].strip().replace(' ','').replace('"','')
            try:
                pop = int(float(pop_raw))
            except Exception:
                continue
            data[canton] = pop
    else:
        # treat as two-column CSV
        for row in rows:
            if not row or len(row) < 2:
                continue
            canton = row[0].strip()
            pop_raw = row[1].strip().replace(' ','').replace('"','')
            try:
                pop = int(float(pop_raw))
            except Exception:
                continue
            data[canton] = pop

    if not data:
        raise ValueError('No valid canton/population rows found in CSV')

    out_path = Path(out_json)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open('w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return data

if __name__ == '__main__':
    # allow running as script from PowerShell:
    import sys
    csv_in = sys.argv[1] if len(sys.argv) > 1 else 'data/raw/pop_by_canton.csv'
    print('Normalizing', csv_in)
    out = normalize_population_csv(csv_in)
    print('Wrote', len(out), 'rows to data/processed/pop_by_canton.json')
