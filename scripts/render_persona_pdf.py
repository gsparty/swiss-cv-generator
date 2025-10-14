import json, os, sys, traceback

try:
    from src.swiss_cv import generators, exporters
except Exception:
    # If exporters missing, still proceed to dump persona
    generators = __import__("src.swiss_cv.generators", fromlist=["*"])
    exporters = None

def _get_persona():
    # prefer JSON-ready wrapper if present
    gen = getattr(generators, "generate_persona_jsonable", None) or getattr(generators, "generate_persona")
    return gen()

def main():
    try:
        persona = _get_persona()
    except Exception:
        traceback.print_exc()
        sys.exit(2)

    # Persona should already be builtins if generate_persona_jsonable exists; if not, convert safely
    def to_builtin(o):
        from types import SimpleNamespace
        if isinstance(o, SimpleNamespace):
            return {k: to_builtin(v) for k, v in vars(o).items()}
        if isinstance(o, dict):
            return {k: to_builtin(v) for k, v in o.items()}
        if isinstance(o, list):
            return [to_builtin(i) for i in o]
        return o

    if not isinstance(persona, (dict, list)):
        persona = to_builtin(persona)

    os.makedirs("out", exist_ok=True)
    html_path = os.path.join("out", "persona_preview.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write("<!doctype html><html><head><meta charset=\"utf-8\"><title>Persona Preview</title></head><body>")
        f.write("<h1>Persona Preview</h1><pre>")
        f.write(json.dumps(persona, ensure_ascii=False, indent=2))
        f.write("</pre></body></html>")
    print("Wrote HTML preview:", html_path)

    # Try to call exporters to make PDF if possible
    if exporters:
        render_fn = getattr(exporters, "render_pdf_from_html_string", None) or getattr(exporters, "render_pdf", None)
        if render_fn:
            out_pdf = os.path.join("out", f"persona_{persona.get('last_name','unknown')}_preview.pdf")
            try:
                ok = render_fn(open(html_path, "r", encoding="utf-8").read(), out_pdf) if render_fn.__code__.co_argcount >= 2 else render_fn(html_path, out_pdf)
                # render_fn might return True/False or None — just report
                print("Attempted PDF render. Output path:", out_pdf)
            except Exception:
                print("PDF rendering failed; see traceback below.")
                traceback.print_exc()
        else:
            print("No known PDF render function found in exporters. Skipping PDF step.")
    else:
        print("No exporters module available. You can use out/persona_preview.html to manually generate PDF.")
    
if __name__ == '__main__':
    main()
