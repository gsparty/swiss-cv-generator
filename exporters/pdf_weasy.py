from jinja2 import Environment, FileSystemLoader, select_autoescape
import os
from pathlib import Path

TEMPLATES_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR), autoescape=select_autoescape(['html','xml']))

def render_html(persona):
    tpl = env.get_template('cv.html')
    return tpl.render(person=persona.dict())

def render_pdf_with_weasy(persona, out_path):
    try:
        from weasyprint import HTML, CSS
    except Exception:
        raise
    html = render_html(persona)
    css_path = os.path.join(TEMPLATES_DIR, 'styles', 'cv.css')
    HTML(string=html).write_pdf(out_path, stylesheets=[CSS(filename=css_path)])
