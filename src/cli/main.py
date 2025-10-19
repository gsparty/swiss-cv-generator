import os
import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from src.personas.persona_builder import build_persona
from src.export.to_json import save_persona_json
from src.export.to_pdf import render_cv_pdf

console = Console()

@click.group()
def cli():
    pass

@cli.command()
@click.option('--count', default=1, type=int, help='Number of CVs to generate')
@click.option('--canton', default='all', help='Canton code (e.g. ZH) or all')
@click.option('--industry', default=None, help='Industry filter (technology, finance, ...)')
@click.option('--language', default=None, help='Force language (de|fr|it)')
@click.option('--format', 'out_format', default='both', type=click.Choice(['json','pdf','both']), help='Output format')
@click.option('--output-dir', default='sample_outputs', help='Where to write files')
@click.option('--verbose', is_flag=True)
def generate(count, canton, industry, language, out_format, output_dir, verbose):
    os.makedirs(output_dir, exist_ok=True)
    console.print('[bold green]Starting generation[/bold green]')
    with Progress(SpinnerColumn(), TextColumn('{task.description}'), BarColumn(), TimeElapsedColumn()) as progress:
        task = progress.add_task('Generating CVs...', total=count)
        for i in range(count):
            persona = build_persona(preferred_canton=canton if canton!='all' else None, preferred_industry=industry)
            # Optionally force language
            if language:
                persona.language = language
            base = f\"{persona.full_name.replace(' ','_')}_{persona.canton}_{i}\"
            if out_format in ('json','both'):
                json_path = os.path.join(output_dir, base + '.json')
                save_persona_json(persona, json_path)
            if out_format in ('pdf','both'):
                pdf_path = os.path.join(output_dir, base + '.pdf')
                render_cv_pdf(persona, pdf_path)
            progress.advance(task)
    console.print('[bold blue]Generation complete[/bold blue]')

if __name__ == '__main__':
    cli()
