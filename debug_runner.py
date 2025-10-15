import sys, os, json, traceback

def safe_print(s):
    try:
        print(s)
    except:
        pass

cwd = os.getcwd()
safe_print("CWD: " + cwd)
src = os.path.join(cwd, "src")
safe_print("src exists: " + str(os.path.exists(src)))
if os.path.exists(src):
    try:
        safe_print("src contents (top-level): " + str(os.listdir(src)))
    except Exception as e:
        safe_print("Could not list src: " + repr(e))

# Add src to sys.path (highest priority)
if src not in sys.path:
    sys.path.insert(0, src)
safe_print("sys.path[0]: " + str(sys.path[0]))
safe_print("first 6 entries of sys.path:")
for p in sys.path[:6]:
    safe_print("  - " + str(p))

# Attempt import and sampling
try:
    from swisscv.generators.sampler import sample_persona_seeded
    safe_print("Imported sampler OK")
    p = sample_persona_seeded(seed=42)
    safe_print(f"Sampled persona: {p.first_name} {p.last_name} | canton={p.canton} | lang={p.language}")
    out_dir = os.path.join(cwd, "out_samples")
    os.makedirs(out_dir, exist_ok=True)
    fname = f"{p.first_name.lower()}_{p.last_name.lower()}_sample.json"
    with open(os.path.join(out_dir, fname), "w", encoding="utf8") as fh:
        json.dump(p.dict(), fh, ensure_ascii=False, indent=2)
    safe_print("Wrote: " + os.path.join(out_dir, fname))
except Exception as e:
    safe_print("IMPORT / RUN ERROR:")
    traceback.print_exc()
