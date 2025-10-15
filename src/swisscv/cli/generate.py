import argparse, time, json, os
from pathlib import Path
from swisscv.generators.sampler import sample_persona_seeded
from swisscv.generators.openai_client import call_openai
from swisscv.generators.pdf_renderer import render_pdf_from_template

PROMPT_DE = "Erstelle eine kurze, professionelle, schweizerische Berufs-Zusammenfassung für {full_name}, mit Fokus auf {industry}."

def render_one(p, outdir: Path, index: int, template_folder="templates/pdf"):
    persona = p.dict() if hasattr(p, "dict") else p.__dict__
    # call openai (or fallback)
    try:
        persona["summary"] = call_openai(PROMPT_DE.format(**persona))
    except Exception:
        persona["summary"] = "Erfahrener Profi mit relevanter Erfahrung und starken technischen Fähigkeiten."
    outdir.mkdir(parents=True, exist_ok=True)
    basename = f"{persona.get('first_name','x')}_{persona.get('last_name','x')}_{index}"
    # choose template by language (de/fr/it)
    lang = persona.get("language","de")
    tpl = Path(template_folder) / f"{lang}.html"
    if not tpl.exists():
        tpl = Path(template_folder) / "de.html"
    out_pdf = outdir / (basename + ".pdf")
    rendered_path = render_pdf_from_template(str(tpl), persona, str(out_pdf))
    # write JSON
    json_path = outdir / (basename + ".json")
    json_path.write_text(json.dumps(persona, ensure_ascii=False, indent=2), encoding="utf8")
    return rendered_path, json_path

def main():
    parser = argparse.ArgumentParser(description="Swiss CV Generator (MVP)")
    parser.add_argument("--count", type=int, default=1, help="How many CVs to generate")
    parser.add_argument("--outdir", type=str, default="out_samples", help="Output directory")
    parser.add_argument("--canton", type=str, default=None, help="Force canton code (e.g. ZH)")
    parser.add_argument("--seed", type=int, default=None, help="Seed for deterministic sampling")
    args = parser.parse_args()

    outdir = Path(args.outdir)
    for i in range(args.count):
        seed = (args.seed + i) if args.seed is not None else int(time.time()) + i
        p = sample_persona_seeded(seed=seed, canton_code=args.canton)
        rendered, jsonfile = render_one(p, outdir, i)
        print(f"Generated: {rendered}  (data: {jsonfile})")

if __name__ == "__main__":
    main()
