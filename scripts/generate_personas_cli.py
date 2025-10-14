import typer
from typing import Optional
import os
from swiss_cv.generator import generate

app = typer.Typer(help="Swiss CV Generator CLI (dev)")

# explicit command name: "generate"
@app.command("generate")
def generate_cmd(
    count: int = typer.Option(5, "--count", "-n", help="Number of personas to generate"),
    seed: Optional[int] = typer.Option(42, "--seed", help="RNG seed for reproducibility"),
    out_dir: str = typer.Option("out_personas_cli", "--out-dir", "-o", help="Output directory"),
    canton: Optional[str] = typer.Option(None, "--canton", "-c", help="Force a specific canton code (e.g. ZH)"),
    industry: Optional[str] = typer.Option(None, "--industry", "-i", help="Force a specific industry"),
    validate: bool = typer.Option(False, "--validate", help="Validate each generated persona against the JSON schema (requires data/schemas/swiss_persona.schema.json)")
):
    schema_path = os.path.join("data", "schemas", "swiss_persona.schema.json")
    created = generate(count=count, seed=seed, out_dir=out_dir, canton=canton, industry=industry, validate_schema=validate, schema_path=schema_path if validate else None)
    typer.echo(f"Created {len(created)} persona JSON file(s) in {out_dir}")
    for p in created:
        typer.echo(" - " + p)

if __name__ == "__main__":
    app()
