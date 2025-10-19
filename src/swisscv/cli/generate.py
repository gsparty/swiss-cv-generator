import argparse, time, json, os, textwrap
from pathlib import Path
from swisscv.generators.sampler import sample_persona_seeded
from swisscv.generators.openai_client import call_openai
from swisscv.generators.pdf_renderer import render_pdf_from_template

PROMPT_DE = "Erstelle eine kurze, professionelle, schweizerische Berufs-Zusammenfassung für {full_name}, mit Fokus auf {industry}."

def _truncate_summary(s: str, max_chars: int) -> str:
    s = s or ""
    if len(s) <= max_chars:
        return s
    # try to end on sentence boundary if possible
    end = s[:max_chars].rfind('. ')
    if end != -1 and end > int(max_chars*0.6):
        return s[:end+1].strip()
    return s[:max_chars].rstrip() + " …"

def render_one(p, outdir: Path, index: int, template_folder="templates/pdf", summary_max_chars=None):
    persona = p.dict() if hasattr(p, "dict") else p.__dict__
    # get summary from OpenAI (or fallback)
    try:
        persona["summary"] = call_openai(PROMPT_DE.format(**persona))
    except Exception:
        persona["summary"] = "Erfahrener Profi mit relevanter Erfahrung und starken technischen Fähigkeiten."

    # If requested, truncate summary for one-page output
    if summary_max_chars is not None:
        persona["summary"] = _truncate_summary(persona.get("summary",""), summary_max_chars)

    outdir.mkdir(parents=True, exist_ok=True)
    basename = f"{persona.get('first_name','x')}_{persona.get('last_name','x')}_{index}"
    # choose template by language (de/fr/it)
    lang = persona.get("language","de")
    tpl = Path(template_folder) / f"{lang}.html"
    if not tpl.exists():
        tpl = Path(template_folder) / "de.html"
    # The pdf_renderer expects (template_path, context, out_path)
    out_pdf = outdir / (basename + ".pdf")
    rendered_path = render_pdf_from_template(str(tpl), persona, str(out_pdf))
    # write JSON
    json_path = outdir / (basename + ".json")
    json_path.write_text(json.dumps(persona, ensure_ascii=False, indent=2), encoding="utf8")
    return rendered_path, json_path

def main(argv=None):
    parser = argparse.ArgumentParser(description="Swiss CV Generator (MVP)")
    parser.add_argument("--count", type=int, default=1, help="How many CVs to generate")
    parser.add_argument("--outdir", type=str, default="out_samples", help="Output directory")
    parser.add_argument("--canton", type=str, default=None, help="Force canton code (e.g. ZH)")
    parser.add_argument("--seed", type=int, default=None, help="Seed for deterministic sampling")

    # New PDF controls
    parser.add_argument("--pdf-engine", choices=["auto","playwright","weasyprint"], default="auto",
                        help="Preferred PDF engine (auto: try WeasyPrint then Playwright)")
    parser.add_argument("--pdf-scale", type=float, default=None,
                        help="Scale factor to pass to PDF renderer (e.g. 0.95 to slightly shrink output)")
    parser.add_argument("--one-page", action="store_true",
                        help="Attempt to force one-page CVs (sets summary truncation and a default scale)")
    parser.add_argument("--summary-max-chars", type=int, default=None,
                        help="Max characters for the generated summary (useful with --one-page)")

    args = parser.parse_args(argv)

    # Apply PDF engine/scale for renderer via environment variables (renderer reads them)
    os.environ["PDF_ENGINE"] = args.pdf_engine
    if args.pdf_scale is not None:
        os.environ["PDF_SCALE"] = str(args.pdf_scale)

    # If one-page requested but no summary max provided, set a conservative default
    summary_max = args.summary_max_chars
    if args.one_page and summary_max is None:
        summary_max = 550  # default truncation to ~550 chars -> ~3 sentences

    # If one-page and no explicit PDF_SCALE set, nudge a smaller scale
    if args.one_page and args.pdf_scale is None:
        # be conservative; user can override with --pdf-scale
        os.environ.setdefault("PDF_SCALE", "0.94")

    outdir = Path(args.outdir)
    for i in range(args.count):
        seed = (args.seed + i) if args.seed is not None else int(time.time()) + i
        p = sample_persona_seeded(seed=seed, canton_code=args.canton)
        rendered, jsonfile = render_one(p, outdir, i, summary_max_chars=summary_max)
        print(f"Generated: {rendered}  (data: {jsonfile})")

if __name__ == "__main__":
    main()


