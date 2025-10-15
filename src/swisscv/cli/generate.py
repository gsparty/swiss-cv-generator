import os
import json
import time
import argparse
from pathlib import Path
from typing import Optional

from rich.progress import track
from swisscv.generators.sampler import sample_persona_seeded
from swisscv.generators.openai_client import call_openai
from swisscv.exporters.pdf_renderer import render_pdf_from_template
from swisscv.utils.contacts import normalize_phone

PROMPTS_DIR = Path(__file__).resolve().parents[3] / "generators" / "prompts"
TEMPLATES_DIR = Path(__file__).resolve().parents[3] / "templates" / "pdf"

LANG_PROMPT_MAP = {
    "de": PROMPTS_DIR / "summary_de.txt",
    # add "fr": PROMPTS_DIR / "summary_fr.txt", "it": ...
}

LANG_TEMPLATE_MAP = {
    "de": TEMPLATES_DIR / "de.html",
    # add fr/it templates later
}

def fill_prompt(template_text: str, persona: dict) -> str:
    # safe simple .format substitution using persona dict
    try:
        return template_text.format(**persona)
    except Exception:
        # fallback: append persona summary block
        return template_text + "\n\n" + json.dumps(persona, ensure_ascii=False)

def make_summary_for_persona(persona: dict) -> str:
    lang = persona.get("language", "de")
    prompt_file = LANG_PROMPT_MAP.get(lang, LANG_PROMPT_MAP["de"])
    if prompt_file.exists():
        template_text = prompt_file.read_text(encoding="utf8")
        prompt = fill_prompt(template_text, persona)
        # call OpenAI wrapper (will fallback if no API key)
        summary = call_openai(prompt)
        # minimal post-process
        return summary.strip()
    return "Profil nicht verfügbar."

def render_one(persona_obj, outdir: Path, index: int):
    # persona_obj may be Pydantic model or dict
    persona = persona_obj.dict() if hasattr(persona_obj, "dict") else dict(persona_obj)
    # normalize contact
    persona["phone"] = normalize_phone(persona.get("phone",""))
    persona["email"] = persona.get("email","").lower()
    persona["full_name"] = persona.get("full_name") or f'{persona.get("first_name","")} {persona.get("last_name","")}'
    # get summary
    persona["summary"] = make_summary_for_persona(persona)
    basename = f"{persona['first_name'].lower()}_{persona['last_name'].lower()}_{index}"
    out_pdf = outdir / f"{basename}.pdf"
    out_json = outdir / f"{basename}.json"
    # choose template
    tpl = LANG_TEMPLATE_MAP.get(persona.get("language","de"), LANG_TEMPLATE_MAP["de"])
    # fill experiences placeholder minimal if absent
    if "experiences" not in persona:
        persona["experiences"] = []
    # render pdf
    render_pdf_from_template(str(tpl), persona, str(out_pdf))
    # write json
    out_json.write_text(json.dumps(persona, ensure_ascii=False, indent=2), encoding="utf8")
    return out_pdf, out_json

def main(argv=None):
    parser = argparse.ArgumentParser(prog="swiss-cv-generate")
    parser.add_argument("--count", type=int, default=1, help="Number of CVs to generate")
    parser.add_argument("--canton", type=str, default=None, help="Filter by canton code (e.g., ZH)")
    parser.add_argument("--language", type=str, default=None, help="Filter by language code (de/fr/it)")
    parser.add_argument("--outdir", type=str, default="out", help="Output directory")
    parser.add_argument("--seed", type=int, default=None, help="Random seed (reproducible)")
    args = parser.parse_args(argv)

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    for i in track(range(args.count), description="Generating CVs"):
        seed = (args.seed or int(time.time())) + i
        p = sample_persona_seeded(seed=seed, canton_code=args.canton)
        # optionally filter by language
        if args.language and p.language != args.language:
            # resample a few times then skip
            retry = 0
            while retry < 5 and p.language != args.language:
                p = sample_persona_seeded(seed=seed + retry + 1, canton_code=args.canton)
                retry += 1
        render_one(p, outdir, i)

if __name__ == "__main__":
    main()
