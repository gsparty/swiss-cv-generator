# src/swiss_cv/exporters.py
from __future__ import annotations

import json
import logging
import os
import shutil
from dataclasses import is_dataclass, asdict
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader, select_autoescape

# Optional backends
try:
    from weasyprint import HTML  # type: ignore
    _WEASY_AVAILABLE = True
except Exception:
    _WEASY_AVAILABLE = False

try:
    import pdfkit  # type: ignore
    _PDFKIT_AVAILABLE = True
except Exception:
    _PDFKIT_AVAILABLE = False

TEMPLATES_DIR = Path(__file__).resolve().parents[2] / "templates"
env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape(["html", "xml"]),
)


def _coerce_to_str(obj: Any) -> str:
    """Return a stable string representation for template output or other objects."""
    if isinstance(obj, str):
        return obj
    try:
        return str(obj)
    except Exception:
        try:
            if hasattr(obj, "__dict__"):
                return json.dumps(_to_serializable(obj.__dict__), ensure_ascii=False, indent=2)
            return json.dumps(_to_serializable(obj), ensure_ascii=False)
        except Exception:
            return repr(obj)


def render_template(template_name: str, context: Dict[str, Any]) -> str:
    tpl = env.get_template(template_name)
    rendered = tpl.render(**context)
    return _coerce_to_str(rendered)


def _write_pdf_with_weasy(html_string: str, out_path: Path) -> None:
    if not _WEASY_AVAILABLE:
        raise RuntimeError("WeasyPrint not available")
    HTML(string=html_string).write_pdf(str(out_path))


def _write_pdf_with_pdfkit(html_string: str, out_path: Path) -> None:
    """
    Use pdfkit with an explicit wkhtmltopdf path when available.
    Try:
      1) environment variable WKHTMLTOPDF_PATH
      2) shutil.which('wkhtmltopdf') or shutil.which('wkhtmltopdf.exe')
      3) common install locations (Program Files)
    """
    if not _PDFKIT_AVAILABLE:
        raise RuntimeError("pdfkit (wkhtmltopdf) not available")

    # 1) check explicit env var
    wk_path = os.environ.get("WKHTMLTOPDF_PATH")
    if wk_path and not os.path.isabs(wk_path):
        wk_path = shutil.which(wk_path) or wk_path

    # 2) try shutil.which for common executables
    if not wk_path:
        wk_path = shutil.which("wkhtmltopdf") or shutil.which("wkhtmltopdf.exe")

    # 3) fallback to common install dirs on Windows
    if not wk_path and os.name == "nt":
        candidates = [
            r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe",
            r"C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe",
        ]
        for c in candidates:
            if os.path.exists(c):
                wk_path = c
                break

    if not wk_path:
        raise RuntimeError(
            "wkhtmltopdf binary not found. Set WKHTMLTOPDF_PATH env var to the full path "
            "or ensure wkhtmltopdf is on PATH."
        )

    # use explicit configuration so pdfkit uses the correct binary
    config = pdfkit.configuration(wkhtmltopdf=wk_path)
    pdfkit.from_string(html_string, str(out_path), configuration=config)


def export_pdf_from_template(
    out_path: str | Path,
    template_name: str,
    context: Dict[str, Any],
    enable_weasy: bool = True,
    enable_pdfkit: bool = True,
) -> Path:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    html_string = render_template(template_name, context)
    html_string = _coerce_to_str(html_string)

    if enable_weasy and _WEASY_AVAILABLE:
        try:
            _write_pdf_with_weasy(html_string, out_path)
            logging.info("Wrote PDF with WeasyPrint -> %s", out_path)
            return out_path
        except Exception as e:
            logging.exception("WeasyPrint failed; will try pdfkit next. Error: %s", e)

    if enable_pdfkit and _PDFKIT_AVAILABLE:
        wk_path = shutil.which("wkhtmltopdf")
        if wk_path:
            try:
                _write_pdf_with_pdfkit(html_string, out_path)
                logging.info("Wrote PDF with wkhtmltopdf -> %s", out_path)
                return out_path
            except Exception as e:
                logging.exception("pdfkit/wkhtmltopdf failed: %s", e)
        else:
            logging.warning("pdfkit present but wkhtmltopdf binary not found on PATH.")

    # Fallback: save HTML file and return that path
    html_fallback = out_path.with_suffix(".html")
    html_fallback.write_text(html_string, encoding="utf-8")
    logging.warning(
        "PDF generation not available. Saved HTML fallback to %s. Install WeasyPrint or wkhtmltopdf to enable PDFs.",
        html_fallback,
    )
    return html_fallback


# ---------------- JSON serialization helper ----------------
def _to_serializable(obj: Any) -> Any:
    """
    Convert object to JSON-serializable Python primitives recursively.
    Handles:
      - SimpleNamespace
      - dataclasses
      - objects with __dict__
      - lists / tuples / sets
      - dicts
      - primitives
    """
    # primitives
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj

    # dataclass
    if is_dataclass(obj):
        try:
            return _to_serializable(asdict(obj))
        except Exception:
            # fallback to vars
            return _to_serializable(vars(obj))

    # SimpleNamespace
    if isinstance(obj, SimpleNamespace):
        return _to_serializable(vars(obj))

    # dict
    if isinstance(obj, dict):
        return {str(k): _to_serializable(v) for k, v in obj.items()}

    # iterable (list/tuple/set)
    if isinstance(obj, (list, tuple, set)):
        return [_to_serializable(v) for v in obj]

    # object with __dict__
    if hasattr(obj, "__dict__"):
        try:
            return _to_serializable(vars(obj))
        except Exception:
            pass

    # fallback to str
    try:
        return str(obj)
    except Exception:
        return repr(obj)


# ----- Public functions expected by CLI -----
def export_json(persona: Dict[str, Any] | Any, out_path: str | Path) -> Path:
    """
    Write persona to a JSON file. Accepts dict or objects; will convert to primitives.
    """
    out = Path(out_path)
    if out.is_dir() or out.suffix == "":
        # name extraction with safe fallback
        name = None
        if isinstance(persona, dict):
            name = persona.get("name")
        else:
            if hasattr(persona, "name"):
                name = getattr(persona, "name")
        safe_name = (name or "persona").replace(" ", "_")
        out = out / f"{safe_name}.json"

    if out.suffix.lower() != ".json":
        out = out.with_suffix(".json")
    out.parent.mkdir(parents=True, exist_ok=True)

    serializable = _to_serializable(persona)
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(serializable, fh, ensure_ascii=False, indent=2)

    logging.info("Wrote JSON -> %s", out)
    return out


def export_pdf(persona: Dict[str, Any] | Any, out_path: str | Path, template_name: str = "cv_de.html") -> Path:
    """
    Export persona to PDF (or HTML fallback). Handles object-like persona inputs.
    """
    out = Path(out_path)
    if out.is_dir() or out.suffix == "":
        # build filename
        name = None
        if isinstance(persona, dict):
            name = persona.get("name")
        else:
            if hasattr(persona, "name"):
                name = getattr(persona, "name")
        safe_name = (name or "persona").replace(" ", "_")
        out = out / f"{safe_name}.pdf"
    if out.suffix.lower() not in [".pdf", ".html"]:
        out = out.with_suffix(".pdf")

    # make persona safe for templates too: convert to dict-like structure
    context_persona = _to_serializable(persona)
    context = {"persona": context_persona, **(context_persona if isinstance(context_persona, dict) else {})}
    result_path = export_pdf_from_template(out, template_name, context)
    logging.info("Exported PDF/HTML -> %s", result_path)
    return result_path
