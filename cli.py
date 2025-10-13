import click
from generators.swiss_persona_generator import SwissPersonaGenerator
from generators.summary_generator import SummaryGenerator
from exporters.json_exporter import export_json
from exporters.pdf_exporter import export_pdf

@click.group()
def cli():
    """Swiss CV Generator CLI"""
    pass

@cli.command()
@click.option('--count', default=1, help='Number of CVs to generate')
@click.option('--format', 'out_format', type=click.Choice(['json','pdf']), default='json')
@click.option('--output-dir', default='output')
@click.option('--include-summary', is_flag=True, help='Include professional summary')
def generate(count, out_format, output_dir, include_summary):
    """Generate N Swiss CVs"""
    gen = SwissPersonaGenerator()
    summarizer = SummaryGenerator()
    for i in range(count):
        persona = gen.generate()
        if include_summary:
            persona.summary = summarizer.generate(persona)
        filename = f"{persona.first_name}_{persona.last_name}_{i+1}.{out_format}"
        path = f"{output_dir}/{filename}"
        if out_format == 'json':
            export_json(persona, path)
        else:
            export_pdf(persona, path)
        click.echo(f"Created {path}")

@cli.command()
def info():
    """Display loader counts"""
    from data_loaders.swiss_data_loader import SwissDataLoader
    loader = SwissDataLoader()
    click.echo(f"Cantons: {len(loader.cantons)}")
    click.echo(f"Occupations: {len(loader.occupations)}")
    click.echo(f"Companies: {len(loader.companies)}")

@cli.command()
def test():
    """Run unit tests"""
    import subprocess
    subprocess.run(['pytest','-q'])

if __name__ == '__main__':
    cli()
