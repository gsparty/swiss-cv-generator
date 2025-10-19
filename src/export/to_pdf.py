from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
from typing import List
from src.data.models import SwissPersona

def render_cv_pdf(persona: SwissPersona, path: str):
    doc = SimpleDocTemplate(path, pagesize=A4, rightMargin=20*mm, leftMargin=20*mm, topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    normal = styles['Normal']
    bullet = styles['Bullet']

    elems: List = []

    # Header
    elems.append(Paragraph(persona.full_name, title_style))
    contact = f"{persona.canton} • {persona.language.value} • {persona.age} Jahre<br/>{persona.email} • {persona.phone}"
    elems.append(Paragraph(contact, normal))
    elems.append(Spacer(1,8))

    # Summary
    elems.append(Paragraph('<b>Profil / Summary</b>', styles['Heading2']))
    elems.append(Paragraph(persona.summary or '', normal))
    elems.append(Spacer(1,8))

    # Experience (simple table)
    elems.append(Paragraph('<b>Berufserfahrung / Experience</b>', styles['Heading2']))
    data = [['Zeitraum','Position','Firma','Beschreibung']]
    for h in persona.career_history:
        start = h.get('start_date','')
        end = h.get('end_date','')
        title = h.get('title','')
        comp = h.get('company','')
        desc = h.get('desc','')
        data.append([f"{start} – {end}", title, comp, desc])
    tbl = Table(data, colWidths=[60*mm, 40*mm, 50*mm, None])
    tbl.setStyle(TableStyle([
        ('GRID',(0,0),(-1,-1),0.25,colors.grey),
        ('BACKGROUND',(0,0),(-1,0),colors.lightgrey),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
    ]))
    elems.append(tbl)
    elems.append(Spacer(1,8))

    # Skills & Languages
    elems.append(Paragraph('<b>Skills</b>', styles['Heading2']))
    elems.append(Paragraph(', '.join(persona.skills), normal))
    elems.append(Spacer(1,6))
    elems.append(Paragraph('<b>Sprachen / Languages</b>', styles['Heading2']))
    elems.append(Paragraph(persona.language.value, normal))

    doc.build(elems)


