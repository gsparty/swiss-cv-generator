# mvp_cli.py (patched) - supports backend selection
import sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import argparse, os, json
from swiss_cv.generator_mvp import generate_persona
from pathlib import Path

def choose_renderer(backend):
    if backend == "weasy":
        try:
            from exporters.pdf_weasy import render_pdf_with_weasy as render
            return render
        except Exception:
            pass
    # try reportlab v2
    try:
        from exporters.pdf_reportlab_v2 import render_person_pdf_reportlab_v2 as render
        return render
    except Exception:
        # fallback to simple renderer
        from exporters.pdf_mvp import render_person_pdf as render
        return render

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--count', type=int, default=1)
    parser.add_argument('--format', choices=['json','pdf','both'], default='both')
    parser.add_argument('--output-dir', default='outputs')
    parser.add_argument('--occupation', default='technology')
    parser.add_argument('--pdf-backend', choices=['reportlab2','weasy','reportlab-simple'], default='reportlab2')
    args = parser.parse_args()

    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)

    render = choose_renderer(args.pdf_backend)

    for i in range(args.count):
        persona = generate_persona(occupation=args.occupation)
        safe_name = f"{persona.first_name.replace(' ','_')}_{persona.last_name.replace(' ','_')}_{i+1}"
        json_path = outdir / (safe_name + '.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(persona.dict(), f, ensure_ascii=False, indent=2)

        if args.format in ('pdf','both'):
            pdf_path = outdir / (safe_name + '.pdf')
            try:
                render(persona, str(pdf_path))
                print(f"Wrote PDF: {pdf_path}")
            except Exception as e:
                print("PDF render failed:", e)
        print(f"Wrote JSON: {json_path}")

if __name__ == '__main__':
    main()


