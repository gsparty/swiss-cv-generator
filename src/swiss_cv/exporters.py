import json
import os

from fpdf import FPDF


def export_json(persona, out_path):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(persona.to_dict(), f, ensure_ascii=False, indent=2)


def export_pdf(persona, out_path):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", size=16)
    pdf.cell(0, 8, f"{persona.first_name} {persona.last_name}", ln=True)
    pdf.set_font("Helvetica", size=11)
    pdf.cell(
        0,
        6,
        f"{persona.occupation} — {persona.canton_name} ({persona.language})",
        ln=True,
    )
    pdf.ln(4)
    pdf.set_font("Helvetica", size=10)
    pdf.multi_cell(0, 6, persona.summary)
    pdf.ln(4)
    pdf.cell(
        0,
        6,
        f"Age: {persona.age}    Experience: {persona.years_experience} years",
        ln=True,
    )
    pdf.cell(0, 6, f"Employer: {persona.employer or '—'}", ln=True)
    pdf.cell(0, 6, f"Email: {persona.email}    Phone: {persona.phone}", ln=True)
    pdf.output(out_path)
