from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Frame, PageTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# Register font fallback
FONT_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'assets', 'fonts', 'DejaVuSans.ttf'))
if not os.path.exists(FONT_PATH):
    alt = os.path.join('C:\\', 'Windows', 'Fonts', 'arial.ttf')
    FONT_PATH = alt if os.path.exists(alt) else None

if FONT_PATH:
    try:
        pdfmetrics.registerFont(TTFont('EmbeddedSans', FONT_PATH))
        BASE_FONT = 'EmbeddedSans'
    except Exception:
        BASE_FONT = 'Helvetica'
else:
    BASE_FONT = 'Helvetica'

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='Name', fontName=BASE_FONT, fontSize=20, leading=22, spaceAfter=6))
styles.add(ParagraphStyle(name='Contact', fontName=BASE_FONT, fontSize=9, leading=11))
styles.add(ParagraphStyle(name='Heading', fontName=BASE_FONT, fontSize=11, leading=13, spaceBefore=6, spaceAfter=4))
styles.add(ParagraphStyle(name='Normal', fontName=BASE_FONT, fontSize=10, leading=12))
styles.add(ParagraphStyle(name='Bullet', fontName=BASE_FONT, fontSize=9, leading=11))

def _build_person_flowables(persona):
    story = []
    # Header area
    fullname = f"{persona.first_name} {persona.last_name}"
    story.append(Paragraph(fullname, styles['Name']))
    contact = f"{persona.email} &#8226; {persona.phone} &#8226; {persona.canton}"
    story.append(Paragraph(contact, styles['Contact']))
    story.append(Spacer(1, 6))

    # Summary
    story.append(Paragraph("Summary", styles['Heading']))
    story.append(Paragraph(persona.summary or '', styles['Normal']))
    story.append(Spacer(1, 6))

    # Experience block
    story.append(Paragraph("Experience", styles['Heading']))
    for exp in persona.experiences:
        title = f"<b>{exp.title}</b> — {exp.company} ({exp.start_year}-{exp.end_year or 'Present'})"
        story.append(Paragraph(title, styles['Normal']))
        if exp.description:
            story.append(Paragraph(exp.description, styles['Bullet']))
    story.append(Spacer(1, 6))

    # Skills (if present in persona.dict)
    skills = getattr(persona, 'skills', None)
    if skills:
        story.append(Paragraph("Skills", styles['Heading']))
        story.append(Paragraph(', '.join(skills), styles['Normal']))
    return story

def render_person_pdf_reportlab_v2(persona, out_path):
    # Two-column layout: left narrow (contact/skills), right wide (summary, experience)
    doc = SimpleDocTemplate(out_path, pagesize=A4, rightMargin=18*mm, leftMargin=18*mm, topMargin=18*mm, bottomMargin=18*mm)
    width, height = A4

    # Left frame: x=leftMargin, width ~70 mm
    left_w = 70 * mm
    gutter = 6 * mm
    right_w = width - doc.leftMargin - doc.rightMargin - left_w - gutter

    left_frame = Frame(doc.leftMargin, doc.bottomMargin, left_w, height - doc.topMargin - doc.bottomMargin, id='left')
    right_frame = Frame(doc.leftMargin + left_w + gutter, doc.bottomMargin, right_w, height - doc.topMargin - doc.bottomMargin, id='right')

    def two_col_page(canvas, doc):
        canvas.setFont(BASE_FONT, 8)
        # You can draw header/footer decorations here if needed

    tpl = PageTemplate(id='TwoCol', frames=[left_frame, right_frame], onPage=two_col_page)
    doc.addPageTemplates([tpl])

    # Build story: we will put everything in right column except contact/skills which we put into left
    # For simplicity: create left flowables then right flowables and combine with frame break markers
    from reportlab.platypus import FrameBreak

    # Build left column (contact + quick facts)
    left_story = []
    left_story.append(Paragraph(f"<b>{persona.first_name} {persona.last_name}</b>", styles['Normal']))
    left_story.append(Spacer(1,4))
    left_story.append(Paragraph(persona.email or '', styles['Contact']))
    left_story.append(Paragraph(persona.phone or '', styles['Contact']))
    left_story.append(Paragraph(persona.canton or '', styles['Contact']))
    left_story.append(Spacer(1,8))
    skills = getattr(persona, 'skills', None)
    if skills:
        left_story.append(Paragraph("Skills", styles['Heading']))
        left_story.append(Paragraph(', '.join(skills), styles['Normal']))

    # Build right column
    right_story = _build_person_flowables(persona)

    # Combine: left story, framebreak, right_story
    story = left_story + [FrameBreak()] + right_story
    doc.build(story)
