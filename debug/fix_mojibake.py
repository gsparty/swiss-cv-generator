import json, os, sys
from pathlib import Path
from ftfy import fix_text

def fix_obj(o):
    if isinstance(o, str):
        return fix_text(o)
    if isinstance(o, list):
        return [fix_obj(x) for x in o]
    if isinstance(o, dict):
        return {fix_obj(k): fix_obj(v) for k,v in o.items()}
    return o

base = Path('outputs_json')
if not base.exists():
    print('No outputs_json directory found; skipping.')
    sys.exit(0)

changed = []
for f in sorted(base.glob('*.json')):
    try:
        s = f.read_text(encoding='utf8', errors='surrogateescape')
        d = json.loads(s)
    except Exception as e:
        # try reading as latin-1 then reparsing
        try:
            s2 = f.read_text(encoding='latin-1')
            d = json.loads(s2)
        except Exception as e2:
            print('Failed to parse', f, e, e2)
            continue
    fixed = fix_obj(d)
    # quick compare
    if json.dumps(fixed, ensure_ascii=False) != json.dumps(d, ensure_ascii=False):
        bak = f.with_suffix('.json.bak')
        f.rename(bak)
        f.write_text(json.dumps(fixed, ensure_ascii=False, indent=2), encoding='utf8')
        changed.append((str(f), str(bak)))
print('Fixed files:', len(changed))
for new,bak in changed[:20]:
    print(' -', new, '(bak:', bak, ')')
