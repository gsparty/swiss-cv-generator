# src/export/pdf_renderer_reportlab.py
"""
Refined ReportLab PDF renderer with improved visual design:
- Larger name (26pt) with accent color
- Right contact card (58mm)
- Thin dividers between experience roles
- Timeline dot + vertical connector for experience entries
- Optional Inter fonts from assets/fonts/Inter-*.ttf (fallback: Helvetica)
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Frame, PageTemplate, FrameBreak,
    Table, TableStyle, Flowable, KeepTogether
)
from reportlab.pdfbase import ttfonts, pdfmetrics
from reportlab.lib.colors import HexColor
from typing import Any, Optional
import datetime
import os

# ---------- Config knobs ----------
ACCENT = "#0050A4"   # accent color
FONT_DIR = os.path.join(os.getcwd(), "assets", "fonts")  # put Inter-Regular.ttf / Inter-Bold.ttf here
FONT_REGULAR = "Inter"
FONT_BOLD = "Inter-Bold"
RIGHT_COL_WIDTH = 58 * mm
DIVIDER_THICKNESS = 0.4
# -----------------------------------

def _register_fonts():
    """Register Inter fonts if present, otherwise fall back to Helvetica."""
    try:
        reg = {}
        reg[FONT_REGULAR] = os.path.join(FONT_DIR, "Inter-Regular.ttf")
        reg[FONT_BOLD] = os.path.join(FONT_DIR, "Inter-Bold.ttf")
        any_reg = False
        for name, path in reg.items():
            if os.path.exists(path):
                pdfmetrics.registerFont(ttfonts.TTFont(name, path))
                any_reg = True
        if any_reg:
            return FONT_REGULAR, FONT_BOLD
    except Exception:
        pass
    return "Helvetica", "Helvetica-Bold"

FONT_REGULAR_USED, FONT_BOLD_USED = _register_fonts()

def _get(p: Any, key: str, default: Optional[str] = "") -> str:
    if p is None:
        return default
    if isinstance(p, dict):
        return p.get(key, default) or default
    return getattr(p, key, default) or default

class ThinDivider(Flowable):
    def __init__(self, width, thickness=DIVIDER_THICKNESS, color=HexColor("#E6E9EC")):
        Flowable.__init__(self)
        self.width = width
        self.thickness = thickness
        self.color = color
        self.height = thickness + 2

    def draw(self):
        self.canv.setLineWidth(self.thickness)
        self.canv.setStrokeColor(self.color)
        self.canv.line(0, 0, self.width, 0)

class TimelineDot(Flowable):
    """
    Draw a small dot and optional vertical connector for timeline visual.
    width param is unused but kept for compatibility with Flowable sizing APIs.
    """
    def __init__(self, dot_diameter=4, connector_height=18, connector_color=HexColor("#E6E9EC")):
        Flowable.__init__(self)
        self.dot_diameter = dot_diameter
        self.connector_height = connector_height
        self.connector_color = connector_color
        self.width = dot_diameter
        self.height = connector_height / 2 + dot_diameter

    def draw(self):
        c = self.canv
        radius = self.dot_diameter / 2.0
        x = radius
        y = self.height - radius
        # dot (filled)
        c.setFillColor(HexColor(ACCENT))
        c.circle(x, y, radius, stroke=0, fill=1)
        # connector line below dot
        c.setStrokeColor(self.connector_color)
        c.setLineWidth(1)
        c.line(x, y - radius, x, y - radius - (self.connector_height - radius))

def _labels_for_lang(lang: str):
    mapping = {
        "de": {"profile": "Profil", "experience": "Berufserfahrung", "education": "Ausbildung", "skills": "Skills", "languages": "Sprachen", "contact": "Kontakt"},
        "fr": {"profile": "Profil", "experience": "Expérience", "education": "Formation", "skills": "Compétences", "languages": "Langues", "contact": "Contact"},
        "it": {"profile": "Profilo", "experience": "Esperienza", "education": "Formazione", "skills": "Competenze", "languages": "Lingue", "contact": "Contatto"},
    }
    return mapping.get((lang or "de").lower()[:2], mapping["de"])

def render_persona_pdf(persona: Any, out_path: str):
    PAGE_SIZE = A4
    PAGE_WIDTH, PAGE_HEIGHT = PAGE_SIZE
    MARGIN = 18 * mm
    GUTTER = 8 * mm
    LEFT_COL_WIDTH = PAGE_WIDTH - 2 * MARGIN - RIGHT_COL_WIDTH - GUTTER

    base = getSampleStyleSheet()
    style_name = ParagraphStyle(
        "Name",
        parent=base["Heading1"],
        fontName=FONT_BOLD_USED,
        fontSize=26,
        leading=28,
        spaceAfter=4,
        textColor=HexColor(ACCENT),
    )
    style_meta = ParagraphStyle(
        "Meta",
        parent=base["Normal"],
        fontName=FONT_REGULAR_USED,
        fontSize=9,
        leading=11,
        textColor=HexColor("#555555"),
        spaceAfter=6,
    )
    style_h = ParagraphStyle(
        "H",
        parent=base["Heading3"],
        fontName=FONT_BOLD_USED,
        fontSize=11,
        spaceBefore=6,
        spaceAfter=6,
        textColor=HexColor(ACCENT)
    )
    style_normal = ParagraphStyle(
        "Body",
        parent=base["BodyText"],
        fontName=FONT_REGULAR_USED,
        fontSize=10,
        leading=13,
        spaceAfter=4
    )
    style_small = ParagraphStyle(
        "Small",
        parent=base["Normal"],
        fontName=FONT_REGULAR_USED,
        fontSize=8,
        leading=10,
        textColor=HexColor("#777777")
    )
    style_bullet = ParagraphStyle(
        "Bullet",
        parent=base["Normal"],
        fontName=FONT_REGULAR_USED,
        fontSize=9.2,
        leftIndent=6,
        leading=12,
    )

    doc = SimpleDocTemplate(out_path, pagesize=PAGE_SIZE,
                            leftMargin=MARGIN, rightMargin=MARGIN,
                            topMargin=MARGIN, bottomMargin=MARGIN)
    left_frame = Frame(MARGIN, MARGIN, LEFT_COL_WIDTH, PAGE_HEIGHT - 2 * MARGIN, id="left")
    right_frame = Frame(MARGIN + LEFT_COL_WIDTH + GUTTER, MARGIN, RIGHT_COL_WIDTH, PAGE_HEIGHT - 2 * MARGIN, id="right")
    doc.addPageTemplates([PageTemplate(id="TwoCol", frames=[left_frame, right_frame])])

    flow = []

    # Header left
    name = _get(persona, "name") or _get(persona, "full_name") or "Unnamed"
    canton = _get(persona, "canton") or ""
    language = _get(persona, "language") or ""
    age = _get(persona, "age") or ""
    contact_email = _get(persona, "email") or ""
    contact_phone = _get(persona, "phone") or ""

    flow.append(Paragraph(name, style_name))
    meta_parts = []
    if canton:
        meta_parts.append(str(canton))
    if language:
        meta_parts.append(str(language))
    if age:
        meta_parts.append(f"{age} Jahre")
    meta = " • ".join(meta_parts)
    if meta:
        flow.append(Paragraph(meta, style_meta))
    contact_line = " • ".join([x for x in (contact_email, contact_phone) if x])
    if contact_line:
        flow.append(Paragraph(contact_line, style_small))
    flow.append(Spacer(1, 6))

    # Summary
    summary = _get(persona, "summary") or _get(persona, "profil") or ""
    labels = _labels_for_lang(language or "de")
    if summary:
        flow.append(Paragraph(labels["profile"], style_h))
        flow.append(Paragraph(summary, style_normal))
        flow.append(Spacer(1, 6))

    # Switch to right column for contact card, skills, languages
    flow.append(FrameBreak())

    # Right column content
    right_flow = []
    # Contact card
    contact_items = []
    contact_items.append([Paragraph(f"<b>{labels['contact']}</b>", style_h)])
    if contact_email:
        contact_items.append([Paragraph(contact_email, style_normal)])
    if contact_phone:
        contact_items.append([Paragraph(contact_phone, style_normal)])
    facts = []
    if language:
        facts.append(f"{language}")
    if canton:
        facts.append(f"{canton}")
    if age:
        facts.append(f"{age} Jahre")
    if facts:
        contact_items.append([Paragraph(" • ".join(facts), style_small)])

    contact_tbl = Table(contact_items, colWidths=[RIGHT_COL_WIDTH - 8])
    contact_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HexColor(ACCENT)),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    right_flow.append(contact_tbl)
    right_flow.append(Spacer(1, 8))

    # Photo placeholder box (keeps right column visually balanced)
    photo_path = _get(persona, "photo_path", "")
    if photo_path and os.path.exists(photo_path):
        from reportlab.platypus import Image
        img = Image(photo_path, width=RIGHT_COL_WIDTH - 8, height=(RIGHT_COL_WIDTH - 8) * 0.6)
        right_flow.append(img)
        right_flow.append(Spacer(1, 8))
    else:
        ph = Table([[Paragraph("Foto", style_small)]], colWidths=[RIGHT_COL_WIDTH - 12], rowHeights=[(RIGHT_COL_WIDTH - 12) * 0.55])
        ph.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 0.6, HexColor("#d0d3d6")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]))
        right_flow.append(ph)
        right_flow.append(Spacer(1, 8))

    # Skills
    skills = _get(persona, "skills") or []
    if isinstance(skills, str):
        skills = [s.strip() for s in skills.split(",") if s.strip()]
    if skills:
        right_flow.append(Paragraph(labels["skills"], style_h))
        # two-column layout inside right column
        data = []
        row = []
        for i, s in enumerate(skills):
            row.append(Paragraph("• " + s, style_bullet))
            if len(row) == 2:
                data.append(row)
                row = []
        if row:
            row.append(Paragraph("", style_bullet))
            data.append(row)
        tbl = Table(data, colWidths=[(RIGHT_COL_WIDTH - 12)/2, (RIGHT_COL_WIDTH - 12)/2])
        tbl.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 6)]))
        right_flow.append(tbl)
        right_flow.append(Spacer(1, 6))

    # Languages
    langs = _get(persona, "languages") or []
    if isinstance(langs, str):
        langs = [s.strip() for s in langs.split(",") if s.strip()]
    if langs:
        right_flow.append(Paragraph(labels["languages"], style_h))
        for L in langs:
            right_flow.append(Paragraph(L, style_normal))
        right_flow.append(Spacer(1, 6))

    # timestamp
    gen_ts = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    right_flow.append(Spacer(1, 6))
    right_flow.append(Paragraph(f"Generiert: {gen_ts}", style_small))

    flow.extend(right_flow)
    flow.append(FrameBreak())

    # Experience (left)
    experiences = _get(persona, "career_history") or _get(persona, "experience") or []
    if isinstance(experiences, dict):
        experiences = list(experiences.values())
    if experiences:
        flow.append(Paragraph(labels["experience"], style_h))
        for i, exp in enumerate(experiences):
            start = exp.get("start", "") if isinstance(exp, dict) else _get(exp, "start", "")
            end = exp.get("end", "") if isinstance(exp, dict) else _get(exp, "end", "")
            period = f"{start} – {end}".strip(" –")
            title = exp.get("title", "") if isinstance(exp, dict) else _get(exp, "title", "")
            comp = exp.get("company", "") if isinstance(exp, dict) else _get(exp, "company", "")
            desc = exp.get("description", "") if isinstance(exp, dict) else _get(exp, "description", "")

            # build a two-column table: date (narrow) + content (wide)
            date_col_width = 36 * mm
            content_col_width = LEFT_COL_WIDTH - date_col_width

            # timeline dot (we draw the dot in the leftmost small cell)
            date_par = Paragraph(f"<b>{period}</b>", style_small)
            content_par = Paragraph(f"<b>{title}</b><br/><i>{comp}</i>", style_normal)

            tbl = Table([[date_par, content_par]], colWidths=[date_col_width, content_col_width])
            tbl.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0,0), (0, -1), 0),
                ("RIGHTPADDING", (0,0), (0, -1), 6),
                ("LEFTPADDING", (1,0), (1, -1), 0),
            ]))
            # KeepTogether to avoid awkward breaks between title and bullets
            flow.append(KeepTogether([tbl]))

            # description bullets
            bullets = []
            if isinstance(desc, str) and desc:
                pieces = [p.strip() for p in desc.replace("\r", "").split("\n") if p.strip()]
                if len(pieces) == 1 and ". " in pieces[0]:
                    pieces = [s.strip() for s in pieces[0].split(". ") if s.strip()]
                bullets = pieces
            for b in bullets:
                flow.append(Paragraph("• " + b, style_bullet))

            # add divider and a small spacer
            flow.append(Spacer(1, 6))
            flow.append(ThinDivider(LEFT_COL_WIDTH))
            flow.append(Spacer(1, 6))

            # Add a small TimelineDot positioned by placing it in a very small table cell
            # We create a single-cell table with the TimelineDot flowable in the left column width
            # and empty content in the right column; the dot will visually overlap near the date.
            # This is a pragmatic approach to ensure the dot is vertically aligned.
            dot = TimelineDot(dot_diameter=4, connector_height=14)
            dot_tbl = Table([[dot, ""]], colWidths=[12, LEFT_COL_WIDTH - 12])
            dot_tbl.setStyle(TableStyle([("LEFTPADDING", (0,0), (-1,-1), 0), ("RIGHTPADDING", (0,0), (-1,-1), 0)]))
            flow.append(dot_tbl)
            flow.append(Spacer(1, 2))

    # Education
    edu = _get(persona, "education") or []
    if edu:
        flow.append(Paragraph(labels["education"], style_h))
        for e in edu:
            what = e.get("degree", "") if isinstance(e, dict) else _get(e, "degree", "")
            at = e.get("institution", "") if isinstance(e, dict) else _get(e, "institution", "")
            when = e.get("when", "") if isinstance(e, dict) else _get(e, "when", "")
            flow.append(Paragraph(f"<b>{what}</b> — {at} <br/><i>{when}</i>", style_normal))
        flow.append(Spacer(1, 6))

    doc.build(flow)
