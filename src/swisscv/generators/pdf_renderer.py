from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

def render_pdf_from_template(template_path: str, context: dict, out_path: str):
    tpl_path = Path(template_path)
    env = Environment(loader=FileSystemLoader(str(tpl_path.parent)), autoescape=select_autoescape(["html","xml"]))
    tpl = env.get_template(tpl_path.name)
    html = tpl.render(**context)
    # Try WeasyPrint
    try:
        from weasyprint import HTML
        HTML(string=html).write_pdf(out_path)
        return out_path
    except Exception:
        # fallback: write HTML alongside expected out_path
        fallback = Path(out_path).with_suffix(".html")
        fallback.write_text(html, encoding="utf8")
        return str(fallback)
