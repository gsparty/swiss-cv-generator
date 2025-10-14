# swiss_cv/exporter.py
import csv
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List

from .content import env

# Try importing WeasyPrint (optional)
try:
    from weasyprint import HTML  # type: ignore

    HAVE_WEASY = True
except Exception:
    HAVE_WEASY = False


def export_json(persona, out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as fh:
        json.dump(persona.dict(), fh, ensure_ascii=False, indent=2)


def render_html(persona, summary: str, lang: str) -> str:
    """
    Render an HTML string from the Jinja template for language `lang`.
    """
    tpl = env.get_template(f"cv_{lang}.html")
    html = tpl.render(persona=persona.dict(), summary=summary)
    return html


def _chrome_paths() -> List[str]:
    """
    Return a list of plausible Chrome/Chromium/Edge executable paths.
    We'll prefer a discovered executable from PATH (shutil.which) first,
    then fall back to common install locations on Windows.
    """
    candidates = []
    # try PATH names
    for name in (
        "chrome",
        "chrome.exe",
        "chromium",
        "chromium.exe",
        "msedge",
        "msedge.exe",
    ):
        p = shutil.which(name)
        if p:
            candidates.append(p)

    # common Windows default locations (won't error if missing)
    candidates += [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files\Chromium\chromium.exe",
        r"C:\Program Files (x86)\Chromium\chromium.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    # return unique existing paths
    seen = set()
    out = []
    for c in candidates:
        if c in seen:
            continue
        seen.add(c)
        out.append(c)
    return out


def _try_chrome_print(infile: Path, outfile: Path) -> bool:
    """
    Attempt to print `infile` to PDF `outfile` using headless Chrome/Edge.
    Returns True on success, False otherwise.
    """
    chrome_bins = _chrome_paths()
    for chrome in chrome_bins:
        if not Path(chrome).exists() and shutil.which(chrome) is None:
            # if the candidate is not a filesystem path and not on PATH, skip
            continue
        cmd = [
            chrome,
            "--headless",
            "--disable-gpu",
            f"--print-to-pdf={str(outfile)}",
            f"file:///{str(infile).replace(chr(92), '/')}",
        ]
        try:
            # run and wait (suppress stdout/stderr unless it fails)
            proc = subprocess.run(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20
            )
            if proc.returncode == 0 and outfile.exists():
                return True
            # continue to next candidate if this one failed
        except Exception:
            continue
    return False


def export_pdf(html: str, out_path: Path):
    """
    Export HTML string to a PDF at out_path.
    Strategy:
      1. If WeasyPrint available, use it.
      2. Else try headless Chrome/Edge.
      3. Else write HTML fallback and inform user.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if HAVE_WEASY:
        try:
            HTML(string=html).write_pdf(str(out_path))
            return
        except Exception as e:
            print(
                "WeasyPrint failed to render PDF, falling back to Chrome if available. Error:",
                e,
            )

    # write temporary HTML file for Chrome to read
    tmp_html = out_path.with_suffix(".html")
    tmp_html.write_text(html, encoding="utf-8")

    # try Chrome/Edge printing
    ok = _try_chrome_print(tmp_html, out_path)
    if ok:
        # optionally remove tmp_html here if you don't want it kept
        try:
            tmp_html.unlink()
        except Exception:
            pass
        return

    # final fallback: leave HTML, report to user
    print(
        "PDF conversion not available (WeasyPrint not installed and no Chrome/Edge found)."
    )
    print(
        f"Wrote HTML to {tmp_html} instead of PDF. To create PDFs automatically, install WeasyPrint or ensure Chrome/Edge is on PATH."
    )


def export_csv(personas: List, out_path: Path):
    """
    Write a CSV summary of personas. Use utf-8-sig so Excel on Windows auto-detects UTF-8.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "name",
        "age",
        "gender",
        "canton",
        "city",
        "language",
        "title",
        "years_experience",
        "email",
        "phone",
    ]
    # Use utf-8-sig so Windows programs detect UTF-8 automatically (writes BOM)
    with out_path.open("w", encoding="utf-8-sig", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for p in personas:
            row = {k: getattr(p, k) for k in fieldnames}
            writer.writerow(row)
