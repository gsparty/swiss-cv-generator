import json
import os
from dataclasses import asdict, is_dataclass

def _persona_to_dict(persona):
    # support pydantic, dataclass, plain dict, or object with __dict__
    if hasattr(persona, "dict") and callable(persona.dict):
        try:
            return persona.dict()
        except Exception:
            pass
    if is_dataclass(persona):
        return asdict(persona)
    if isinstance(persona, dict):
        return persona
    if hasattr(persona, "__dict__"):
        return vars(persona)
    # last resort: try to serialize direct
    return persona

def export_json(persona, path):
    data = {"schema_version": "1.0", "persona": _persona_to_dict(persona)}
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)

def export_pdf(html_string, out_path):
    """
    Try to use the top-level exporters/pdf_renderer.render_pdf_from_html_string if available,
    otherwise fallback to ReportLab, otherwise write HTML to disk.
    Returns True if a PDF was produced, False if fallback HTML was written.
    """
    # Prefer the shared exporters/pdf_renderer if present
    try:
        from exporters.pdf_renderer import render_pdf_from_html_string
        ok = render_pdf_from_html_string(html_string, out_path)
        return ok
    except Exception:
        pass

    # Fallback: try ReportLab minimal writer (registering no fonts here)
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont

        # Try common Windows fonts (optional)
        candidates = [
            r"C:\Windows\Fonts\arial.ttf",
            r"C:\Windows\Fonts\ARIAL.TTF",
            r"C:\Windows\Fonts\DejaVuSans.ttf"
        ]
        font_path = next((p for p in candidates if os.path.exists(p)), None)
        font_name = "Helvetica"
        if font_path:
            try:
                pdfmetrics.registerFont(TTFont("FallbackFont", font_path))
                font_name = "FallbackFont"
            except Exception:
                font_name = "Helvetica"

        c = canvas.Canvas(out_path, pagesize=A4)
        textobject = c.beginText(40, 800)
        textobject.setFont(font_name, 11)
        for line in html_string.splitlines():
            textobject.textLine(line[:120])
        c.drawText(textobject)
        c.save()
        return True
    except Exception as e:
        # final fallback: save HTML for manual conversion
        fallback = out_path.replace(".pdf", ".html")
        with open(fallback, "w", encoding="utf-8") as fh:
            fh.write(html_string)
        return False
