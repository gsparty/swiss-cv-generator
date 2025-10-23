from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from typing import List
from src.data.models import SwissPersona

# Swiss professional colors
COLORS = {
    'primary': colors.HexColor('#2C3E50'),
    'accent': colors.HexColor('#3498DB'),
    'light_gray': colors.HexColor('#ECF0F1'),
    'text': colors.HexColor('#34495E'),
    'light_text': colors.HexColor('#7F8C8D'),
}

def render_cv_pdf(persona: SwissPersona, path: str):
    """Render professional 2-column Swiss CV layout"""
    
    doc = SimpleDocTemplate(
        path,
        pagesize=A4,
        rightMargin=15*mm,
        leftMargin=15*mm,
        topMargin=15*mm,
        bottomMargin=15*mm
    )
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=COLORS['primary'],
        spaceAfter=2,
        fontName='Helvetica-Bold'
    )
    
    section_header_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=11,
        textColor=COLORS['primary'],
        spaceAfter=8,
        spaceBefore=8,
        fontName='Helvetica-Bold',
        borderPadding=5,
        backColor=COLORS['light_gray']
    )
    
    job_title_style = ParagraphStyle(
        'JobTitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=COLORS['accent'],
        fontName='Helvetica-Bold',
        spaceAfter=2
    )
    
    company_style = ParagraphStyle(
        'Company',
        parent=styles['Normal'],
        fontSize=9,
        textColor=COLORS['text'],
        fontName='Helvetica',
        spaceAfter=1
    )
    
    date_style = ParagraphStyle(
        'Date',
        parent=styles['Normal'],
        fontSize=8,
        textColor=COLORS['light_text'],
        fontName='Helvetica-Oblique',
        spaceAfter=3
    )
    
    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontSize=9,
        textColor=COLORS['text'],
        spaceAfter=6,
        leading=12
    )
    
    skill_style = ParagraphStyle(
        'Skill',
        parent=styles['Normal'],
        fontSize=8,
        textColor=COLORS['text'],
        spaceAfter=4,
        leading=10
    )
    
    contact_style = ParagraphStyle(
        'Contact',
        parent=styles['Normal'],
        fontSize=8,
        textColor=COLORS['text'],
        spaceAfter=4,
        leading=11
    )
    
    language_style = ParagraphStyle(
        'Language',
        parent=styles['Normal'],
        fontSize=8,
        textColor=COLORS['text'],
        spaceAfter=2,
        leading=10
    )
    
    # LEFT COLUMN
    left_content = []
    
    left_content.append(Paragraph('<b>KONTAKT</b>', section_header_style))
    full_name = getattr(persona, 'full_name', 'Name')
    left_content.append(Paragraph(f"<b>{full_name}</b>", contact_style))
    
    age = getattr(persona, 'age', 'N/A')
    left_content.append(Paragraph(f"{age} Jahre", contact_style))
    left_content.append(Spacer(1, 3))
    
    phone = getattr(persona, 'phone', 'N/A')
    left_content.append(Paragraph(f"<b>Telefon:</b> {phone}", contact_style))
    
    email = getattr(persona, 'email', 'N/A')
    left_content.append(Paragraph(f"<b>E-Mail:</b> {email}", contact_style))
    
    canton = getattr(persona, 'canton', 'ZH')
    left_content.append(Paragraph(f"<b>Kanton:</b> {canton}", contact_style))
    left_content.append(Spacer(1, 8))
    
    left_content.append(Paragraph('<b>SPRACHEN</b>', section_header_style))
    language = getattr(persona, 'language', 'DE')
    left_content.append(Paragraph(f"{language.upper()} - Muttersprache", language_style))
    left_content.append(Paragraph("Englisch - Flussig", language_style))
    left_content.append(Spacer(1, 8))
    
    left_content.append(Paragraph('<b>FAEHIGKEITEN</b>', section_header_style))
    skills = getattr(persona, 'skills', [])
    for skill in skills[:8]:
        left_content.append(Paragraph(f"• {skill}", skill_style))
    left_content.append(Spacer(1, 6))
    
    # RIGHT COLUMN
    right_content = []
    
    right_content.append(Paragraph(full_name, title_style))
    current_title = getattr(persona, 'current_title', 'Position')
    right_content.append(Paragraph(current_title, job_title_style))
    right_content.append(Spacer(1, 6))
    
    summary = getattr(persona, 'summary', '')
    if summary:
        right_content.append(Paragraph('<b>PROFIL</b>', section_header_style))
        right_content.append(Paragraph(summary, normal_style))
        right_content.append(Spacer(1, 6))
    
    right_content.append(Paragraph('<b>BERUFSERFAHRUNG</b>', section_header_style))
    
    career_history = getattr(persona, 'career_history', [])
    for i, exp in enumerate(career_history[:5]):
        title = exp.get('title', 'Position') if isinstance(exp, dict) else 'Position'
        company = exp.get('company', 'Unternehmen') if isinstance(exp, dict) else 'Unternehmen'
        start_date = exp.get('start_date', '') if isinstance(exp, dict) else ''
        end_date = exp.get('end_date', 'aktuell') if isinstance(exp, dict) else 'aktuell'
        desc = exp.get('desc', '') if isinstance(exp, dict) else ''
        
        right_content.append(Paragraph(title, job_title_style))
        right_content.append(Paragraph(company, company_style))
        right_content.append(Paragraph(f"{start_date} – {end_date}", date_style))
        right_content.append(Paragraph(desc, normal_style))
        
        if i < len(career_history) - 1:
            right_content.append(Spacer(1, 4))
    
    right_content.append(Spacer(1, 6))
    
    education = getattr(persona, 'education', [])
    if education:
        right_content.append(Paragraph('<b>AUSBILDUNG</b>', section_header_style))
        for edu in education[:3]:
            degree = edu.get('degree', 'Abschluss') if isinstance(edu, dict) else 'Abschluss'
            field = edu.get('field_of_study', 'Fachbereich') if isinstance(edu, dict) else 'Fachbereich'
            institution = edu.get('institution', 'Institution') if isinstance(edu, dict) else 'Institution'
            end_year = edu.get('end_year', '') if isinstance(edu, dict) else ''
            
            right_content.append(Paragraph(f"{degree} in {field}", job_title_style))
            right_content.append(Paragraph(institution, company_style))
            right_content.append(Paragraph(f"{end_year}", date_style))
            right_content.append(Spacer(1, 4))
    
    # CREATE 2-COLUMN TABLE
    left_frame_width = 55*mm
    right_frame_width = 125*mm
    
    table_data = [[left_content, right_content]]
    
    main_table = Table(
        table_data,
        colWidths=[left_frame_width, right_frame_width],
        rowHeights=[None]
    )
    
    main_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (0, -1), 0),
        ('RIGHTPADDING', (0, 0), (0, -1), 10),
        ('LEFTPADDING', (1, 0), (1, -1), 10),
        ('RIGHTPADDING', (1, 0), (1, -1), 0),
        ('BACKGROUND', (0, 0), (0, -1), COLORS['light_gray']),
        ('BORDER', (0, 0), (-1, -1), 0, colors.white),
    ]))
    
    elements = [main_table]
    doc.build(elements)
