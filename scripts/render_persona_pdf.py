import json, os, sys, traceback
from types import SimpleNamespace

# Import project modules
try:
    from src.swiss_cv import generators, exporters
except Exception:
    generators = __import__("src.swiss_cv.generators", fromlist=["*"])
    # try to import exporters module; if not found, set to None
    try:
        from src.swiss_cv import exporters
    except Exception:
        exporters = None

def to_builtin(o):
    """Recursively convert SimpleNamespace/dict/list into builtin types for JSON serialization."""
    if isinstance(o, SimpleNamespace):
        return {k: to_builtin(v) for k, v in vars(o).items()}
    if isinstance(o, dict):
        return {k: to_builtin(v) for k, v in o.items()}
    if isinstance(o, list):
        return [to_builtin(i) for i in o]
    return o

def get_persona():
    gen = getattr(generators, "generate_persona_jsonable", None) or getattr(generators, "generate_persona")
    return gen()

def main():
    try:
        persona = get_persona()
    except Exception:
        traceback.print_exc()
        sys.exit(2)

    # Make sure persona is JSON-serializable builtins
    if not isinstance(persona, (dict, list)):
        persona_b = to_builtin(persona)
    else:
        persona_b = persona

    os.makedirs("out", exist_ok=True)

    # Write JSON using exporters.export_json if available, else raw dump
    json_name = f"persona_{persona_b.get('last_name','unknown')}.json"
    json_path = os.path.join("out", json_name)
    try:
        if exporters and hasattr(exporters, "export_json"):
            exporters.export_json(persona_b, json_path)
            print("Wrote JSON via exporters.export_json:", json_path)
        else:
            with open(json_path, "w", encoding="utf-8") as fh:
                json.dump({"schema_version":"1.0","persona": persona_b}, fh, ensure_ascii=False, indent=2)
            print("Wrote JSON:", json_path)
    except Exception:
        print("Failed to write JSON, falling back to raw dump.")
        traceback.print_exc()

    # Create a basic HTML preview
    html_name = f"persona_{persona_b.get('last_name','unknown')}.html"
    html_path = os.path.join("out", html_name)
    html_string = "<!doctype html><html><head><meta charset=\"utf-8\"><title>Persona Preview</title></head><body>"
    html_string += "<h1>Persona Preview</h1><pre>"
    html_string += json.dumps(persona_b, ensure_ascii=False, indent=2)
    html_string += "</pre></body></html>"
    with open(html_path, "w", encoding="utf-8") as fh:
        fh.write(html_string)
    print("Wrote HTML preview:", html_path)

    # Try to render PDF using exporters.export_pdf(html_string, out_path)
    pdf_name = f"persona_{persona_b.get('last_name','unknown')}.pdf"
    pdf_path = os.path.join("out", pdf_name)
    try:
        if exporters and hasattr(exporters, "export_pdf"):
            ok = exporters.export_pdf(html_string, pdf_path)
            if ok:
                print("PDF created:", pdf_path)
            else:
                print("exporters.export_pdf returned False — saved fallback HTML instead of PDF.")
        else:
            print("No exporters.export_pdf available — kept HTML at", html_path)
    except Exception:
        print("PDF rendering failed; traceback:")
        traceback.print_exc()

if __name__ == '__main__':
    main()
