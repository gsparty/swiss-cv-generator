import sys, os, json, traceback, csv
from types import SimpleNamespace

# Try to import project generators/exporters
try:
    from src.swiss_cv import generators, exporters
except Exception:
    generators = __import__("src.swiss_cv.generators", fromlist=["*"])
    try:
        from src.swiss_cv import exporters
    except Exception:
        exporters = None

# Try to import reportlab for fallback PDF generation
_have_reportlab = False
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    _have_reportlab = True
except Exception:
    _have_reportlab = False

def to_builtin(o):
    if isinstance(o, SimpleNamespace):
        return {k: to_builtin(v) for k, v in vars(o).items()}
    if isinstance(o, dict):
        return {k: to_builtin(v) for k, v in o.items()}
    if isinstance(o, list):
        return [to_builtin(i) for i in o]
    return o

CSV_FIELDS = [
    "index","first_name","last_name","age","years_experience","primary_language",
    "canton","city","phone","email","title","industry","json_path","html_path","pdf_path"
]

def ensure_csv_header(csv_path):
    if not os.path.exists(csv_path):
        with open(csv_path, "w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
            writer.writeheader()

def append_csv_row(csv_path, row):
    with open(csv_path, "a", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        writer.writerow(row)

def simple_pdf_from_text(text, out_path):
    """Fallback PDF creation using reportlab (writes text lines)."""
    if not _have_reportlab:
        raise RuntimeError("reportlab not available for PDF fallback")
    c = canvas.Canvas(out_path, pagesize=A4)
    width, height = A4
    margin = 40
    y = height - margin
    c.setFont("Helvetica", 10)
    for line in text.splitlines():
        # wrap long lines simply
        if len(line) <= 120:
            c.drawString(margin, y, line)
            y -= 12
        else:
            # naive wrap
            for i in range(0, len(line), 120):
                c.drawString(margin, y, line[i:i+120])
                y -= 12
        if y < margin + 20:
            c.showPage()
            c.setFont("Helvetica", 10)
            y = height - margin
    c.save()
    return True

def save_persona(persona_obj, index, out_dir):
    persona = persona_obj if isinstance(persona_obj, dict) else to_builtin(persona_obj)
    last = persona.get('last_name', f'unknown_{index}')
    safe_last = "".join(ch if ch.isalnum() else "_" for ch in last)
    base = os.path.join(out_dir, f"{index}_{safe_last}")
    os.makedirs(out_dir, exist_ok=True)

    # JSON path
    json_path = f"{base}.json"
    try:
        if exporters and hasattr(exporters, "export_json"):
            exporters.export_json(persona, json_path)
        else:
            with open(json_path, "w", encoding="utf-8") as fh:
                json.dump({'schema_version':'1.0','persona': persona}, fh, ensure_ascii=False, indent=2)
    except Exception:
        traceback.print_exc()

    # HTML path (simple pretty print HTML)
    html_path = f"{base}.html"
    html = "<!doctype html><html><head><meta charset=\"utf-8\"><title>Persona</title></head><body>"
    html += "<h1>Persona</h1><pre>" + json.dumps(persona, ensure_ascii=False, indent=2) + "</pre></body></html>"
    with open(html_path, "w", encoding="utf-8") as fh:
        fh.write(html)

    # PDF path: try exporters.export_pdf(html_string, out_path) else fallback ReportLab simple text PDF
    pdf_path = f"{base}.pdf"
    try:
        if exporters and hasattr(exporters, "export_pdf"):
            ok = exporters.export_pdf(html, pdf_path)
            if not ok:
                # fallback
                if _have_reportlab:
                    simple_pdf_from_text(json.dumps(persona, ensure_ascii=False, indent=2), pdf_path)
        else:
            # no exporters - use reportlab fallback if available
            if _have_reportlab:
                simple_pdf_from_text(json.dumps(persona, ensure_ascii=False, indent=2), pdf_path)
            else:
                # cannot create PDF - leave HTML only
                pdf_path = ""
    except Exception:
        traceback.print_exc()
        # as last resort try reportlab
        try:
            if _have_reportlab:
                simple_pdf_from_text(json.dumps(persona, ensure_ascii=False, indent=2), pdf_path)
        except Exception:
            traceback.print_exc()
            pdf_path = ""

    return json_path, html_path, pdf_path, persona

def main():
    out_dir = "out"
    n = 3
    if len(sys.argv) > 1:
        try:
            n = int(sys.argv[1])
        except Exception:
            pass
    # csv file path
    csv_path = os.path.join(out_dir, "personas.csv")
    os.makedirs(out_dir, exist_ok=True)
    ensure_csv_header(csv_path)

    for i in range(1, n+1):
        try:
            # prefer JSON-ready wrapper if present
            gen = getattr(generators, "generate_persona_jsonable", None) or getattr(generators, "generate_persona")
            p = gen()
            json_path, html_path, pdf_path, persona = save_persona(p, i, out_dir)
            row = {
                "index": i,
                "first_name": persona.get("first_name",""),
                "last_name": persona.get("last_name",""),
                "age": persona.get("age",""),
                "years_experience": persona.get("years_experience",""),
                "primary_language": persona.get("primary_language",""),
                "canton": persona.get("canton",""),
                "city": persona.get("city",""),
                "phone": persona.get("phone",""),
                "email": persona.get("email",""),
                "title": persona.get("title",""),
                "industry": persona.get("industry",""),
                "json_path": json_path,
                "html_path": html_path,
                "pdf_path": pdf_path
            }
            append_csv_row(csv_path, row)
            print(f"Generated: {json_path}, {html_path}, {pdf_path}")
        except Exception:
            traceback.print_exc()

if __name__ == '__main__':
    main()
