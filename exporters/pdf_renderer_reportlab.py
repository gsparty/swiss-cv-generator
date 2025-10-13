from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def render_pdf_from_html_string(html_string, out_path):
    c = canvas.Canvas(out_path, pagesize=A4)
    textobject = c.beginText(40, 800)
    for line in html_string.splitlines():
        textobject.textLine(line[:120])
    c.drawText(textobject)
    c.save()
    return True
