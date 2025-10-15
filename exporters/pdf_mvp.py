from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# try to register a local font (DejaVu) or fall back to a common system font
FONT_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'assets', 'fonts', 'DejaVuSans.ttf'))
if not os.path.exists(FONT_PATH):
    alt = os.path.join('C:\\', 'Windows', 'Fonts', 'arial.ttf')
    FONT_PATH = alt if os.path.exists(alt) else None

if FONT_PATH:
    try:
        pdfmetrics.registerFont(TTFont('EmbeddedSans', FONT_PATH))
        DEFAULT_FONT = 'EmbeddedSans'
    except Exception:
        DEFAULT_FONT = 'Helvetica'
else:
    DEFAULT_FONT = 'Helvetica'

def render_person_pdf(persona, out_path):
    c = canvas.Canvas(out_path, pagesize=A4)
    w, h = A4

    # Header: name and contact
    c.setFont(DEFAULT_FONT if DEFAULT_FONT else 'Helvetica', 18)
    c.drawString(30 * mm, (h - 30 * mm), f"{persona.first_name} {persona.last_name}")
    c.setFont(DEFAULT_FONT if DEFAULT_FONT else 'Helvetica', 10)
    c.drawString(30 * mm, (h - 37 * mm), f"{persona.email}  |  {persona.phone}  |  {persona.canton}")

    # Summary
    text = c.beginText(30 * mm, (h - 50 * mm))
    text.setFont(DEFAULT_FONT if DEFAULT_FONT else 'Helvetica', 10)
    summary = persona.summary or ''
    for line in summary.splitlines():
        text.textLine(line)
    c.drawText(text)

    # Experience
    y = h - 80 * mm
    c.setFont(DEFAULT_FONT if DEFAULT_FONT else 'Helvetica', 12)
    c.drawString(30 * mm, y, "Experience")
    y -= 8 * mm
    for exp in persona.experiences:
        c.setFont(DEFAULT_FONT if DEFAULT_FONT else 'Helvetica', 10)
        c.drawString(32 * mm, y, f"{exp.title} — {exp.company} ({exp.start_year}-{exp.end_year or 'Present'})")
        y -= 6 * mm
        desc = (exp.description or '')[:200]
        c.setFont(DEFAULT_FONT if DEFAULT_FONT else 'Helvetica', 9)
        c.drawString(34 * mm, y, desc)
        y -= 8 * mm

    c.showPage()
    c.save()
