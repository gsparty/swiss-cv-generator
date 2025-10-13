import json
from pathlib import Path
from typing import List
from .content import env
import csv

try:
    from weasyprint import HTML
    HAVE_WEASY = True
except Exception:
    HAVE_WEASY = False


def export_json(persona, out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as fh:
        json.dump(persona.dict(), fh, ensure_ascii=False, indent=2)


def render_html(persona, summary: str, lang: str) -> str:
    tpl = env.get_template(f"cv_{lang}.html")
    html = tpl.render(persona=persona.dict(), summary=summary)
    return html


def export_pdf(html: str, out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if HAVE_WEASY:
        HTML(string=html).write_pdf(str(out_path))
    else:
        # fallback: write HTML and warn
        html_file = out_path.with_suffix(".html")
        with html_file.open("w", encoding="utf-8") as fh:
            fh.write(html)
        print(f"WeasyPrint not installed — wrote HTML to {html_file} instead of PDF.")


def export_csv(personas: List, out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "name",
        "age",
        "gender",
        "canton",
        "city",
        "language",
        "title",
        "years_experience",
        "email",
        "phone",
    ]
    with out_path.open("w", encoding="utf-8", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for p in personas:
            row = {k: getattr(p, k) for k in fieldnames}
            writer.writerow(row)
