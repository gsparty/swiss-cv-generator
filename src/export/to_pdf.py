from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from src.data.models import SwissPersona
import re

COLORS = {
    'primary': colors.HexColor('#2C3E50'),
    'accent': colors.HexColor('#3498DB'),
    'sidebar': colors.HexColor('#ECF0F1'),
    'text': colors.HexColor('#2C3E50'),
    'light': colors.HexColor('#7F8C8D'),
}

def clean_markdown(text):
    if not text:
        return text
    text = re.sub(r'#{1,6}\s*', '', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'^\d+\.\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'^-\s*', '', text, flags=re.MULTILINE)
    return text.strip()

def render_cv_pdf(persona, path):
    doc = SimpleDocTemplate(path, pagesize=A4, rightMargin=10*mm, leftMargin=10*mm, topMargin=10*mm, bottomMargin=10*mm)
    styles = getSampleStyleSheet()
    
    name_style = ParagraphStyle('Name', parent=styles['Normal'], fontSize=26, textColor=COLORS['primary'], fontName='Helvetica-Bold', spaceAfter=20, alignment=TA_LEFT)
    section_style = ParagraphStyle('Section', parent=styles['Normal'], fontSize=9, textColor=colors.white, fontName='Helvetica-Bold', backColor=COLORS['primary'], leftIndent=0, rightIndent=0, spaceAfter=5, spaceBefore=3, leading=12)
    normal_style = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=8.5, textColor=COLORS['text'], spaceAfter=3, leading=11, leftIndent=0)
    bullet_style = ParagraphStyle('Bullet', parent=styles['Normal'], fontSize=8, textColor=COLORS['text'], spaceAfter=3, leading=11, leftIndent=8)
    exp_title_style = ParagraphStyle('ExpTitle', parent=styles['Normal'], fontSize=9.5, textColor=COLORS['accent'], fontName='Helvetica-Bold', spaceAfter=1)
    company_style = ParagraphStyle('Company', parent=styles['Normal'], fontSize=8.5, textColor=COLORS['text'], spaceAfter=0.5)
    date_style = ParagraphStyle('Date', parent=styles['Normal'], fontSize=7.5, textColor=COLORS['light'], fontName='Helvetica-Oblique', spaceAfter=2)
    desc_style = ParagraphStyle('Desc', parent=styles['Normal'], fontSize=8.5, textColor=COLORS['text'], spaceAfter=4, leading=11, leftIndent=8)
    
    left = []
    left.append(Paragraph('KONTAKT', section_style))
    full_name = getattr(persona, 'full_name', 'Name')
    left.append(Paragraph(full_name, normal_style))
    age = getattr(persona, 'age', 'N/A')
    left.append(Paragraph(f'{age} Jahre', normal_style))
    left.append(Spacer(1, 2))
    phone = getattr(persona, 'phone', 'N/A')
    left.append(Paragraph(phone, normal_style))
    email = getattr(persona, 'email', 'N/A')
    left.append(Paragraph(email, normal_style))
    canton = getattr(persona, 'canton', 'ZH')
    left.append(Paragraph(f'Kanton {canton}', normal_style))
    left.append(Spacer(1, 5))
    
    left.append(Paragraph('SPRACHEN', section_style))
    language = getattr(persona, 'language', 'de')
    lang_names = {'de': 'Deutsch', 'fr': 'Franzoesisch', 'it': 'Italienisch', 'en': 'Englisch'}
    main_lang = lang_names.get(language.lower(), 'Deutsch')
    left.append(Paragraph(f'{main_lang} - Muttersprache', normal_style))
    left.append(Paragraph('Englisch - Flüssig', normal_style))
    left.append(Spacer(1, 5))
    
    left.append(Paragraph('KOMPETENZEN', section_style))
    skills = getattr(persona, 'skills', [])
    for skill in skills[:10]:
        clean_skill = clean_markdown(str(skill))
        if not clean_skill or len(clean_skill) < 3:
            continue
        if any(x in clean_skill.lower() for x in ['technische', 'soft skills', 'fähigkeiten', 'für einen']):
            continue
        left.append(Paragraph(f'• {clean_skill}', bullet_style))
    
    right = []
    right.append(Paragraph(full_name, name_style))
    right.append(Spacer(1, 8))
    
    summary = getattr(persona, 'summary', '')
    if summary:
        right.append(Paragraph('PROFESSIONELLES PROFIL', section_style))
        clean_summary = clean_markdown(summary)
        right.append(Paragraph(clean_summary, desc_style))
        right.append(Spacer(1, 3))
    
    right.append(Paragraph('BERUFSERFAHRUNG', section_style))
    career = getattr(persona, 'career_history', [])
    for i, exp in enumerate(career[:5]):
        if not isinstance(exp, dict):
            continue
        title = exp.get('title', 'Position')
        company = exp.get('company', 'Unternehmen')
        start = exp.get('start_date', '')
        end = exp.get('end_date', 'heute')
        desc = exp.get('desc', '')
        clean_desc = clean_markdown(desc)
        right.append(Paragraph(title, exp_title_style))
        right.append(Paragraph(company, company_style))
        right.append(Paragraph(f'{start} - {end}', date_style))
        right.append(Paragraph(clean_desc, desc_style))
        if i < len(career) - 1:
            right.append(Spacer(1, 2))
    
    right.append(Spacer(1, 3))
    education = getattr(persona, 'education', [])
    if education:
        right.append(Paragraph('AUSBILDUNG', section_style))
        for edu in education[:2]:
            if not isinstance(edu, dict):
                continue
            degree = edu.get('degree', 'Abschluss')
            field = edu.get('field_of_study', 'Fachbereich')
            institution = edu.get('institution', 'Institution')
            year = edu.get('end_year', '')
            right.append(Paragraph(f'{degree} in {field}', exp_title_style))
            right.append(Paragraph(institution, company_style))
            right.append(Paragraph(str(year), date_style))
            right.append(Spacer(1, 2))
    
    table = Table([[left, right]], colWidths=[50*mm, 140*mm])
    table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (0, -1), 0),
        ('RIGHTPADDING', (0, 0), (0, -1), 8),
        ('LEFTPADDING', (1, 0), (1, -1), 8),
        ('RIGHTPADDING', (1, 0), (1, -1), 0),
        ('BACKGROUND', (0, 0), (0, -1), COLORS['sidebar']),
        ('BORDER', (0, 0), (-1, -1), 0, colors.white),
    ]))
    doc.build([table])
