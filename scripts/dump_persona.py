from src.swiss_cv.generators import generate_persona
import json
from types import SimpleNamespace

def to_builtin(o):
    # Recursively convert SimpleNamespace / dict / list into JSON-serializable builtins
    if isinstance(o, SimpleNamespace):
        return {k: to_builtin(v) for k, v in vars(o).items()}
    if isinstance(o, dict):
        return {k: to_builtin(v) for k, v in o.items()}
    if isinstance(o, list):
        return [to_builtin(i) for i in o]
    # basic types (str, int, float, bool, None) pass through
    return o

if __name__ == "__main__":
    try:
        p = generate_persona()
    except Exception as e:
        import traceback, sys
        traceback.print_exc()
        sys.exit(2)

    pb = to_builtin(p)
    print(json.dumps(pb, ensure_ascii=False, indent=2))
    import os
    os.makedirs("out", exist_ok=True)
    with open("out/test_persona.json", "w", encoding="utf-8") as f:
        json.dump(pb, f, ensure_ascii=False, indent=2)
    print("Wrote out/test_persona.json")
