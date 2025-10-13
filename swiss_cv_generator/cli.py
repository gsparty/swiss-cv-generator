from pathlib import Path
from typing import List

import click
from rich.progress import Progress

from .content import OpenAITextGenerator
from .exporter import export_csv, export_json, export_pdf, render_html
from .persona import build_persona

VALID_FORMATS = ["pdf", "json", "html", "csv"]


def sanitize_filename(name: str) -> str:
    return "".join(
        c if c.isalnum() or c in (" ", "_", "-") else "_" for c in name
    ).replace(" ", "_")


@click.group()
def cli():
    """Swiss CV Generator CLI"""
    pass


@cli.command()
@click.option(
    "--count", default=1, show_default=True, type=int, help="Number of CVs to generate"
)
@click.option(
    "--language", default=None, help="Preferred language: de/fr/it (optional)"
)
@click.option(
    "--format",
    "formats",
    type=click.Choice(VALID_FORMATS),
    multiple=True,
    default=("pdf", "csv"),
    help="Output formats (can pass multiple times)",
)
@click.option("--output-dir", default="out", show_default=True, help="Output directory")
@click.option(
    "--use-llm/--no-llm",
    default=False,
    help="Enable OpenAI LLM for richer summaries (optional)",
)
def generate(
    count: int, language: str, formats: List[str], output_dir: str, use_llm: bool
):
    """
    Generate one or multiple CVs.

    Example: python -m swiss_cv_generator.cli generate --count 3 --language de --format pdf --format csv --output-dir out
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    llm = OpenAITextGenerator(enabled=use_llm)

    generated_personas = []
    pdf_count = 0

    with Progress() as progress:
        task = progress.add_task("[green]Generating personas...", total=count)
        for i in range(count):
            persona = build_persona(language=language)
            summary = llm.generate_summary(persona)
            generated_personas.append(persona)

            base_name = f"cv_{i+1}_{sanitize_filename(persona.name)}"
            base_path = out / base_name

            if "json" in formats:
                export_json(persona, base_path.with_suffix(".json"))

            # Always render HTML (needed for pdf/html)
            html = render_html(persona, summary, persona.language)
            if "html" in formats:
                (base_path.with_suffix(".html")).write_text(html, encoding="utf-8")

            if "pdf" in formats:
                export_pdf(html, base_path.with_suffix(".pdf"))
                pdf_count += 1

            progress.advance(task)

    # export CSV summary if requested
    if "csv" in formats:
        csv_path = out / "personas_summary.csv"
        export_csv(generated_personas, csv_path)

    click.echo(
        f"Done. Generated {len(generated_personas)} personas. Output directory: {out.resolve()}"
    )


if __name__ == "__main__":
    cli()
