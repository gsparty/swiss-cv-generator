import json
import sys
import os
from pathlib import Path

# Ensure repository root is on sys.path so "src" package imports work when running the script directly.
# This inserts the repo root (parent of scripts/) at index 0.
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from src.data_loaders.bfs_pxweb import fetch_and_save_px, try_extract_1d_series

API_URL = "https://pxweb.bfs.admin.ch/api/v1/en/px-x-0103010000_499"
# Best-effort query: year 2023 and restrict to permanent resident population, total citizenship and total sex.
PAYLOAD = {
    "query": [
        {"code": "Year", "selection": {"filter": "item", "values": ["2023"]}},
        {"code": "Population type", "selection": {"filter": "item", "values": ["Permanent resident population"]}},
        {"code": "Citizenship", "selection": {"filter": "item", "values": ["Citizenship - total"]}},
        {"code": "Sex", "selection": {"filter": "item", "values": ["Sex - total"]}}
    ],
    "response": {"format": "json"}
}

def main():
    print("Repo root used for imports:", repo_root)
    print("Querying BFS PXWeb endpoint:", API_URL)
    try:
        saved = fetch_and_save_px(API_URL, PAYLOAD, prefix="pop_by_canton_2023", out_dir="data/raw/")
        print("Saved raw PX response to:", saved)
    except Exception as e:
        print("Failed to fetch PX data:", str(e))
        print("If this fails, open the dataset page in the browser to build the API query interactively:")
        print("https://www.pxweb.bfs.admin.ch/pxweb/en/px-x-0103010000_499/-/px-x-0103010000_499.px/")
        sys.exit(1)

    # Try to load the saved file and auto-extract a 1D series (canton -> population)
    try:
        with open(saved, "r", encoding="utf-8") as f:
            resp = json.load(f)
        series = try_extract_1d_series(resp)
        # normalize keys: strip whitespace, keep as-is labels (they are human-readable)
        out = {k.strip(): int(v) for k, v in series.items()}
        out_path = Path("data/processed/pop_by_canton.json")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
        print("Wrote normalized canton population to data/processed/pop_by_canton.json (rows: {})".format(len(out)))
    except Exception as ex:
        print("Automatic 1D extraction failed:", str(ex))
        print("Raw px response saved at:", saved)
        print("Open that file and inspect 'dimension' and 'value' keys to craft a custom normalizer, or paste the filename here and I will generate the normalizer for you.")
        sys.exit(2)

if __name__ == "__main__":
    main()
