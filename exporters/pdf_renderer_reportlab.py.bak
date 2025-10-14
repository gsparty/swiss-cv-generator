# exporters/pdf_renderer_reportlab.py
# ReportLab-based PDF renderer for swiss-cv-generator (Unicode-aware, simple Swiss CV layout)
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Frame, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import enums
import os

# register DejaVuSans for full unicode support
FONT_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "fonts", "DejaVuSans.ttf")
if not os.path.exists(FONT_PATH):
    # fallback: try relative repo path
    FONT_PATH = os.path.abspath(os.path.join(os.getcwd(), "assets", "fonts", "DejaVuSans.ttf"))

try:
    pdfmetrics.registerFont(TTFont("DejaVuSans", FONT_PATH))
except Exception as e:
    # if registration fails, fallback to built-in Helvetica
    print("Could not register DejaVuSans, fallback to Helvetica:", e)
    DEFAULT_FONT = "Helvetica"
else:
    DEFAULT_FONT = "DejaVuSans"

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    name="Name",
    fontName=DEFAULT_FONT,
    fontSize=20,
    leading=24,
    spaceAfter=6,
    alignment=enums.TA_LEFT,
))
styles.add(ParagraphStyle(
    name="Heading",
    fontName=DEFAULT_FONT,
    fontSize=11,
    leading=13,
# DEBUG: show resolved FONT_PATH and DEFAULT_FONT at import time
try:
    _dbg_fp = FONT_PATH if 'FONT_PATH' in globals() else None
    _dbg_df = DEFAULT_FONT if 'DEFAULT_FONT' in globals() else None
    print(f"[DEBUG] pdf_renderer_reportlab FONT_PATH={_dbg_fp} DEFAULT_FONT={_dbg_df}")
except Exception:
    pass

    spaceBefore=6,
    spaceAfter=4,
    textColor="#333333",
    backColor=None,
    alignment=enums.TA_LEFT,
    bold=True
))
styles.add(ParagraphStyle(
    name="Normal",
    fontName=DEFAULT_FONT,
    fontSize=10,
    leading=12,
))
styles.add(ParagraphStyle(
    name="Bullet",
    fontName=DEFAULT_FONT,
    fontSize=10,
    leading=12,
    leftIndent=8,
    bulletIndent=0,
))

def _safe_get(d, key, default=""):
    return d.get(key, default) if isinstance(d, dict) else default

def render_pdf(persona, output_path):
    """
    persona: dict-like object with keys: name, canton, language, email, phone, summary, career_history (list)
    output_path: path to write PDF
    """
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                            rightMargin=18*mm, leftMargin=18*mm, topMargin=18*mm, bottomMargin=18*mm)
    story = []

    name = _safe_get(persona, "name", "Unnamed")
    contact_lines = []
    email = _safe_get(persona, "email")
    phone = _safe_get(persona, "phone")
    canton = _safe_get(persona, "canton")
    if email: contact_lines.append(email)
    if phone: contact_lines.append(phone)
    if canton: contact_lines.append(f"Canton: {canton}")

    story.append(Paragraph(name, styles["Name"]))
    for cl in contact_lines:
        story.append(Paragraph(cl, styles["Normal"]))
    story.append(Spacer(1, 6))

    summary = _safe_get(persona, "summary", "")
    if summary:
        story.append(Paragraph("<b>Professional summary</b>", styles["Heading"]))
        story.append(Paragraph(summary, styles["Normal"]))
        story.append(Spacer(1, 6))

    # Experience section
    career = _safe_get(persona, "career_history", [])
    if career:
        story.append(Paragraph("<b>Experience</b>", styles["Heading"]))
        for entry in career:
            title = _safe_get(entry, "title", _safe_get(entry, "role", "Role"))
            company = _safe_get(entry, "company", "")
            period = _safe_get(entry, "period", "")
            header = f"<b>{title}</b> — {company} <i>{period}</i>"
            story.append(Paragraph(header, styles["Normal"]))
            bullets = _safe_get(entry, "bullets", _safe_get(entry, "description", []))
            if isinstance(bullets, str):
                story.append(Paragraph(bullets, styles["Normal"]))
            else:
                for b in bullets:
                    story.append(Paragraph(f"• {b}", styles["Bullet"]))
            story.append(Spacer(1, 4))

    # Skills / Languages
    skills = _safe_get(persona, "skills", [])
    languages = _safe_get(persona, "languages", [])
    if skills or languages:
        story.append(Paragraph("<b>Skills & Languages</b>", styles["Heading"]))
        if skills:
            story.append(Paragraph(", ".join(skills), styles["Normal"]))
        if languages:
            story.append(Paragraph("Languages: " + ", ".join(languages), styles["Normal"]))

    # Build
    try:
        doc.build(story)
    except Exception as e:
        # if anything fails, fallback to writing a very simple text-based PDF
        from reportlab.pdfgen import canvas
        c = canvas.Canvas(output_path, pagesize=A4)
        c.setFont(DEFAULT_FONT if DEFAULT_FONT else "Helvetica", 12)
        c.drawString(40, 800, name)
        c.drawString(40, 780, "Failed to render full layout; minimal PDF generated")
        c.save()
        raise

