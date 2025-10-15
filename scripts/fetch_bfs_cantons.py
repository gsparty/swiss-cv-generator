"""
Fetch canton dataset (JSON/CSV) and write to data/official/cantons.json

Usage:
  python scripts/fetch_bfs_cantons.py --url <DATA_URL> --out data/official/cantons.json

Notes:
- If you know the exact BFS open-data dataset URL, pass it to --url.
- This script simply downloads a JSON/CSV and writes a canonical JSON file.
- If your source is CSV, the script will try to interpret columns named "code","name","population","workforce","lang_*".
"""
import argparse
import json
from pathlib import Path
import requests
import csv
from io import StringIO

def write_json(out_path: Path, data):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf8")
    print(f"Wrote {out_path}")

def fetch_and_write(url: str, out_path: Path):
    print(f"Fetching {url} ...")
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    ctype = r.headers.get("content-type","")
    if "json" in ctype or url.lower().endswith(".json"):
        data = r.json()
        # heuristic: if it's an object with a list under a key, try to extract
        if isinstance(data, dict):
            # attempt common keys
            for k in ("data","features","records","value"):
                if k in data and isinstance(data[k], list):
                    data = data[k]
                    break
        write_json(out_path, data)
    else:
        # assume CSV
        s = r.content.decode("utf8")
        reader = csv.DictReader(StringIO(s))
        rows = [row for row in reader]
        write_json(out_path, rows)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="URL to download canton dataset (JSON or CSV)")
    parser.add_argument("--out", default="data/official/cantons.json", help="Output path")
    args = parser.parse_args()
    fetch_and_write(args.url, Path(args.out))

if __name__ == "__main__":
    main()
