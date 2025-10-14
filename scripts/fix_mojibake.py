#!/usr/bin/env python3
# scripts/fix_mojibake.py
"""
Recursively fix mojibake/encoding problems in JSON files using ftfy.
Usage:
  python scripts/fix_mojibake.py --dir outputs --rename
"""

import argparse
import json
import os
from ftfy import fix_text
from typing import Any

def fix_obj(obj: Any) -> Any:
    """Recursively fix all strings in a JSON-like object."""
    if isinstance(obj, str):
        return fix_text(obj)
    elif isinstance(obj, list):
        return [fix_obj(x) for x in obj]
    elif isinstance(obj, dict):
        return {fix_obj(k) if isinstance(k, str) else k: fix_obj(v) for k,v in obj.items()}
    else:
        return obj

def process_file(path: str, rename: bool=False):
    with open(path, 'rb') as f:
        raw = f.read()
    # Try to decode as utf-8; if it fails, try latin-1 then fix text.
    try:
        s = raw.decode('utf-8')
    except Exception:
        try:
            s = raw.decode('latin-1')
        except Exception:
            s = raw.decode('utf-8', errors='replace')
    try:
        data = json.loads(s)
    except Exception as e:
        print(f"[SKIP] {path} — not valid JSON ({e})")
        return
    fixed = fix_obj(data)
    # write back as UTF-8 with pretty printing
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(fixed, f, ensure_ascii=False, indent=2)
    print(f"[FIXED] {path}")

    if rename and isinstance(fixed, dict):
        # heuristic: rename files if they have first_name / last_name fields
        first = fixed.get('first_name') or fixed.get('firstname') or fixed.get('given_name')
        last = fixed.get('last_name') or fixed.get('lastname') or fixed.get('family_name')
        if first and last:
            # construct a safe filename
            safe = f"{first.strip().replace(' ','_')}_{last.strip().replace(' ','_')}"
            dir_ = os.path.dirname(path)
            ext = os.path.splitext(path)[1]
            dest = os.path.join(dir_, safe + ext)
            # avoid overwriting
            if dest != path:
                if not os.path.exists(dest):
                    os.rename(path, dest)
                    print(f"[RENAMED] {path} -> {dest}")
                else:
                    print(f"[RENAME SKIP] {dest} already exists; left {path}")

def walk_and_fix(directory: str, rename: bool=False):
    for root, dirs, files in os.walk(directory):
        for fn in files:
            if fn.lower().endswith('.json'):
                p = os.path.join(root, fn)
                process_file(p, rename=rename)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', default='outputs', help='Directory to scan for JSON files')
    parser.add_argument('--rename', action='store_true', help='Rename files based on first_name/last_name if present')
    args = parser.parse_args()
    if not os.path.isdir(args.dir):
        print(f"Directory not found: {args.dir}")
        raise SystemExit(1)
    walk_and_fix(args.dir, rename=args.rename)
    print("Done.")
