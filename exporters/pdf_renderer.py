import os

def render_pdf_from_html_string(html_string, out_path):
    # Try WeasyPrint first (best visual fidelity)
    try:
        from weasyprint import HTML
        HTML(string=html_string).write_pdf(out_path)
        return True
    except Exception as e:
        print("WeasyPrint not usable (will fallback to ReportLab):", e)

    # Fallback: ReportLab (better than nothing; tries to register a Unicode TTF)
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont

        # Try common Windows font locations for Arial / DejaVuSans
        candidate_fonts = [
            r"C:\Windows\Fonts\arial.ttf",
            r"C:\Windows\Fonts\ARIAL.TTF",
            r"C:\Windows\Fonts\DejaVuSans.ttf",
            r"C:\Windows\Fonts\DejaVuSans.ttf"
        ]
        font_path = next((p for p in candidate_fonts if os.path.exists(p)), None)
        if font_path:
            try:
                pdfmetrics.registerFont(TTFont("FallbackFont", font_path))
                font_name = "FallbackFont"
            except Exception as fe:
                print("Failed to register TTF, using Helvetica:", fe)
                font_name = "Helvetica"
        else:
            font_name = "Helvetica"

        c = canvas.Canvas(out_path, pagesize=A4)
        textobject = c.beginText(40, 800)
        textobject.setFont(font_name, 11)
        # naive plaintext rendering (strip tags if present)
        # If HTML contains tags, they will appear; for better results, render HTML->text first.
        for line in html_string.splitlines():
            # ensure the line is not too long per row
            textobject.textLine(line[:120])
        c.drawText(textobject)
        c.save()
        return True
    except Exception as e2:
        print("ReportLab fallback failed, saving HTML instead:", e2)
        # Final fallback: save HTML for manual conversion
        fallback = out_path.replace(".pdf", ".html")
        with open(fallback, "w", encoding="utf-8") as fh:
            fh.write(html_string)
        return False

