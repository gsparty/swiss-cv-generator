from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
import os, uuid

def _render_html_to_file(template_path: str, context: dict) -> Path:
    tpl_path = Path(template_path)
    env = Environment(loader=FileSystemLoader(str(tpl_path.parent)), autoescape=select_autoescape(["html","xml"]))
    tpl = env.get_template(tpl_path.name)
    html = tpl.render(**context)
    tmp_name = f"render_{uuid.uuid4().hex}.html"
    tmp_path = tpl_path.parent / tmp_name
    tmp_path.write_text(html, encoding="utf8")
    return tmp_path

def _try_playwright_file(html_file: Path, out_path: str) -> bool:
    try:
        from playwright.sync_api import sync_playwright
        scale = 1.0
        try:
            scale = float(os.environ.get("PDF_SCALE", "1.0"))
        except Exception:
            scale = 1.0
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            page = browser.new_page()
            file_url = html_file.resolve().as_uri()
            page.goto(file_url, wait_until="networkidle")
            header_template = '<div style="width:100%; font-size:9pt; text-align:center;"><span style="font-weight:600;">Lebenslauf</span></div>'
            footer_template = '<div style="width:100%; font-size:9pt; text-align:center;"><span>Seite <span class="pageNumber"></span> / <span class="totalPages"></span></div>'
            page.pdf(path=out_path, format="A4", print_background=True,
                     margin={"top":"18mm","bottom":"18mm","left":"14mm","right":"14mm"},
                     display_header_footer=True,
                     header_template=header_template,
                     footer_template=footer_template,
                     scale=scale)
            browser.close()
        return True
    except Exception:
        return False

def _try_weasyprint_html(html_file: Path, out_path: str) -> bool:
    try:
        from weasyprint import HTML
        HTML(filename=str(html_file)).write_pdf(out_path)
        return True
    except Exception:
        return False

def render_pdf_from_template(template_path: str, context: dict, out_path: str):
    out_path = str(out_path)
    html_file = _render_html_to_file(template_path, context)
    engine = os.environ.get("PDF_ENGINE", "auto").lower()
    try:
        if engine == "playwright":
            if _try_playwright_file(html_file, out_path):
                html_file.unlink(missing_ok=True)
                return out_path
        elif engine == "weasyprint":
            if _try_weasyprint_html(html_file, out_path):
                html_file.unlink(missing_ok=True)
                return out_path
            if _try_playwright_file(html_file, out_path):
                html_file.unlink(missing_ok=True)
                return out_path
        else:
            if _try_weasyprint_html(html_file, out_path):
                html_file.unlink(missing_ok=True)
                return out_path
            if _try_playwright_file(html_file, out_path):
                html_file.unlink(missing_ok=True)
                return out_path
    finally:
        try:
            html_file.unlink(missing_ok=True)
        except Exception:
            pass

    fallback = Path(out_path).with_suffix(".html")
    fallback.write_text(Path(html_file).read_text(encoding="utf8"), encoding="utf8")
    return str(fallback)


