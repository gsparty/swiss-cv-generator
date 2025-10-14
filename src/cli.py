﻿import os
import random
from pathlib import Path

import click
from rich.console import Console

from .swiss_cv.data_loaders import (load_cantons, load_companies,
                                    load_occupations, sample_weighted)
from .swiss_cv.exporters import export_json, export_pdf
from .swiss_cv.generators import generate_persona

console = Console()


@click.group()
def cli():
    """Swiss CV Generator CLI"""
    pass


@cli.command()
@click.option("--count", "-n", default=1, type=int, help="Number of CVs to generate")
@click.option(
    "--output-dir", "-o", default="outputs", type=click.Path(), help="Output directory"
)
@click.option(
    "--format",
    "-f",
    default="pdf,json",
    help="Output formats: comma separated (pdf,json)",
)
@click.option("--seed", default=None, type=int, help="Random seed for reproducibility")
def generate(count, output_dir, format, seed):
    """Generate synthetic Swiss CVs"""
    if seed is not None:
        random.seed(seed)
    formats = [p.strip().lower() for p in format.split(",") if p.strip()]
    os.makedirs(output_dir, exist_ok=True)

    cantons = load_cantons()
    occupations = load_occupations()
    companies = load_companies()

    for i in range(count):
        canton = sample_weighted(cantons, "workforce")
        occupation = random.choice(occupations)
        # choose a company in same canton if possible
        same = [c for c in companies if c.get("canton") == canton.get("id")]
        company = random.choice(same) if same else random.choice(companies)
        persona = generate_persona(
            canton=canton, occupation=occupation, company=company
        )
        base = f"{persona.first_name}_{persona.last_name}_{i+1}".replace(" ", "_")
        if "json" in formats:
            out_json = os.path.join(output_dir, base + ".json")
            export_json(persona, out_json)
            console.log(f"Wrote JSON ? {out_json}")
        if "pdf" in formats:
            out_pdf = os.path.join(output_dir, base + ".pdf")
            export_pdf(persona, out_pdf)
            console.log(f"Wrote PDF  ? {out_pdf}")


if __name__ == "__main__":
    cli()

