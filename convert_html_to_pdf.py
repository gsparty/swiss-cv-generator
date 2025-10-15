from pathlib import Path
from playwright.sync_api import sync_playwright
import sys

# directory path or default to current folder
dirpath = sys.argv[1] if len(sys.argv) > 1 else "."
p = Path(dirpath)

html_files = list(p.glob("*.html"))
if not html_files:
    print("No .html files found in", p.resolve())
    sys.exit(0)

with sync_playwright() as pw:
    browser = pw.chromium.launch()
    for f in html_files:
        try:
            html = f.read_text(encoding="utf8")
            page = browser.new_page()
            page.set_content(html, wait_until="networkidle")
            out_pdf = f.with_suffix(".pdf")
            page.pdf(path=str(out_pdf), format="A4", print_background=True)
            print("Wrote:", out_pdf)
        except Exception as e:
            print("Failed to convert", f, "->", e)
    browser.close()
