from swiss_cv.models import SwissPersona
from swiss_cv.data_loaders.bfs_loader import fetch_bfs_table_by_id
import json
import os
import traceback

# 1) write schema
schema_json_text = SwissPersona.schema_json(indent=2)
os.makedirs("data/schemas", exist_ok=True)
schema_path = os.path.join("data", "schemas", "swiss_persona.schema.json")
with open(schema_path, "w", encoding="utf8") as f:
    f.write(schema_json_text)
print(f"Wrote {schema_path}")

# 2) fetch BFS example table (population by canton)
out_csv = os.path.join("data", "raw", "canton_population_2010_2024_pxwebpy.csv")
errors = []
for lang in ["en", "de", "fr", "it"]:
    try:
        print(f"Attempting to fetch table in language: {lang}")
        df = fetch_bfs_table_by_id("px-x-0102010000_101", out_csv, language=lang, retry=2)
        print(f"Success: saved to {out_csv} (rows: {len(df)})")
        break
    except Exception as e:
        tb = traceback.format_exc()
        print(f"Failed for language {lang}: {e}")
        errors.append((lang, str(e)))
        # continue to next language
else:
    print("All attempted languages failed. See error summary:")
    for lang, err in errors:
        print(f" - {lang}: {err}")
    # if a raw JSON was written by the loader, mention it
    raw_candidates = [p for p in os.listdir("data/raw") if p.endswith(".raw.json")]
    if raw_candidates:
        print("Found raw JSON(s) in data/raw/:")
        for r in raw_candidates:
            print(" -", r)
    print("Exiting with failure status.")
