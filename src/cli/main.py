import click
from src.personas.persona_builder import build_persona
from src.export.to_json import save_persona_json
from src.export.to_pdf import render_cv_pdf
from pathlib import Path
from rich.console import Console
from rich.progress import Progress

console = Console()

@click.group()
def cli():
    """Swiss CV Generator - Generate authentic Swiss CVs"""
    pass

@cli.command()
@click.option('--count', default=1, type=int, help='Number of CVs to generate')
@click.option('--canton', default='all', help='Canton code (ZH, BE, GE, etc.) or "all"')
@click.option('--industry', default='all', help='Industry (technology, finance, healthcare, etc.)')
@click.option('--language', default='de', type=click.Choice(['de', 'fr', 'it']), help='Language')
@click.option('--format', default='both', type=click.Choice(['json', 'pdf', 'both']), help='Output format')
@click.option('--output-dir', default='output', help='Output directory path')
@click.option('--verbose', is_flag=True, help='Enable verbose logging')
def generate(count, canton, industry, language, format, output_dir, verbose):
    """Generate Swiss CVs with specified parameters"""
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    console.print(f"[cyan]Generating {count} CVs[/cyan]")
    console.print(f"  Canton: {canton}")
    console.print(f"  Industry: {industry}")
    console.print(f"  Language: {language}")
    console.print(f"  Format: {format}")
    console.print(f"  Output: {output_dir}")
    console.print()
    
    with Progress() as progress:
        task = progress.add_task("[cyan]Generating CVs...", total=count)
        
        for i in range(count):
            try:
                preferred_canton = None if canton == 'all' else canton
                preferred_industry = None if industry == 'all' else industry
                
                persona = build_persona(
                    preferred_canton=preferred_canton,
                    preferred_industry=preferred_industry,
                    
                )
                
                filename = f"{persona.first_name}_{persona.last_name}_{persona.canton}_{i}"
                
                if format in ['json', 'both']:
                    json_path = Path(output_dir) / f"{filename}.json"
                    save_persona_json(persona, str(json_path))
                    if verbose:
                        console.print(f"  ? Saved JSON: {json_path}")
                
                if format in ['pdf', 'both']:
                    pdf_path = Path(output_dir) / f"{filename}.pdf"
                    render_cv_pdf(persona, str(pdf_path))
                    if verbose:
                        console.print(f"  ? Saved PDF: {pdf_path}")
                
                progress.update(task, advance=1)
                
            except Exception as e:
                console.print(f"[red]? Error generating CV {i}: {str(e)[:100]}[/red]")
                if verbose:
                    raise
    
    console.print(f"\n[green]? Generation complete! ({count} CVs)[/green]")
    console.print(f"  Output: {Path(output_dir).absolute()}")

@cli.command()
def validate():
    """Validate data files and setup"""
    console.print("[cyan]Validating setup...[/cyan]")
    
    required_files = [
        'data/cantons.json',
        'data/companies.json',
        'data/occupations.json',
        'data/names_de.csv',
        'data/names_fr.csv',
        'data/names_it.csv',
        'data/surnames.csv'
    ]
    
    all_valid = True
    for file in required_files:
        if Path(file).exists():
            console.print(f"  ? {file}")
        else:
            console.print(f"  ? {file} [red]MISSING[/red]")
            all_valid = False
    
    if all_valid:
        console.print("\n[green]? All data files present![/green]")
    else:
        console.print("\n[red]? Some files are missing. Check setup.[/red]")

if __name__ == '__main__':
    cli()
