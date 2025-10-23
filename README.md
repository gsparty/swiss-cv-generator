# Swiss CV Generator 🇨🇭

Generate realistic, culturally authentic Swiss CVs with authentic Swiss demographic data and OpenAI-powered content generation.

## ✨ Features

- **Demographic Accuracy**: Population-weighted canton sampling with realistic age-to-experience correlations
- **Cultural Authenticity**: Language-appropriate names, Swiss contact patterns, industry-specific career progression
- **Multilingual**: Support for German (DE), French (FR), and Italian (IT)
- **Professional Output**: JSON and PDF exports with polished Swiss CV layouts
- **OpenAI Integration**: AI-powered professional summaries with fallback templates
- **Flexible Filtering**: Generate CVs by canton, industry, language

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- OpenAI API key (optional - uses fallback if unavailable)

### Installation

```bash
# Clone repository
git clone https://github.com/gsparty/swiss-cv-generator.git
cd swiss-cv-generator

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
# or: source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### Configuration

```bash
# Copy environment template
copy .env.example .env

# Add your OpenAI API key (optional)
notepad .env
# Set: OPENAI_API_KEY=sk-...
```

### Generate Your First CV

```bash
# Generate 1 German CV
python -m src.cli.main generate --count 1 --language de

# Check output
dir sample_outputs/
```

## 📖 Usage Guide

### Basic Generation

```bash
# Generate single CV (German)
python -m src.cli.main generate --count 1 --language de

# Generate 10 CVs (French)
python -m src.cli.main generate --count 10 --language fr

# Generate 5 CVs (Italian)
python -m src.cli.main generate --count 5 --language it
```

### Filter by Canton

```bash
# Generate 5 Zurich CVs
python -m src.cli.main generate --count 5 --canton ZH

# Generate 10 Geneva CVs
python -m src.cli.main generate --count 10 --canton GE

# Geneva cantons: ZH, BE, GE, BS, BL, AG, SO, LU, UR, SZ, OW, NW, GL, AR, AI, SG, TG, TI, VD, VS, NE, JU
```

### Filter by Industry

```bash
# Generate tech CVs
python -m src.cli.main generate --count 10 --industry technology

# Generate finance CVs
python -m src.cli.main generate --count 5 --industry finance

# Available industries: technology, finance, healthcare, manufacturing, retail, hospitality, education, construction, pharma, insurance, consulting, logistics
```

### Output Formats

```bash
# Generate as JSON only
python -m src.cli.main generate --count 5 --format json

# Generate as PDF only
python -m src.cli.main generate --count 5 --format pdf

# Generate both JSON and PDF (default)
python -m src.cli.main generate --count 5 --format both
```

### Custom Output Directory

```bash
# Save to custom location
python -m src.cli.main generate --count 10 --output-dir ./my_cvs

# Output: ./my_cvs/Firstname_Lastname_CA_0.json, etc.
```

### Verbose Mode

```bash
# Show detailed generation progress
python -m src.cli.main generate --count 5 --verbose
```

### Complete Example

```bash
# Generate 20 Zurich tech CVs in German, both formats, verbose
python -m src.cli.main generate \
  --count 20 \
  --canton ZH \
  --industry technology \
  --language de \
  --format both \
  --output-dir ./zurich_tech_cvs \
  --verbose
```

## 🔍 Validation

Check that all required data files are present:

```bash
python -m src.cli.main validate
```

Output:
```
Validating setup...
  ✓ data/cantons.json
  ✓ data/companies.json
  ✓ data/occupations.json
  ✓ data/names_de.csv
  ✓ data/names_fr.csv
  ✓ data/names_it.csv
  ✓ data/surnames.csv

✓ All data files present!
```

## 📂 Output Formats

### JSON Output

```json
{
  "first_name": "Luca",
  "last_name": "Meier",
  "full_name": "Luca Meier",
  "canton": "ZH",
  "language": "de",
  "age": 35,
  "birth_year": 1990,
  "gender": "male",
  "experience_years": 12,
  "industry": "technology",
  "current_title": "Senior Technology",
  "email": "luca.meier@example.ch",
  "phone": "+41 79 123 45 67",
  "professional_summary": "Erfahrener Software-Entwickler...",
  "work_experience": [...],
  "education": [...],
  "skills": ["Python", "React", "Database Design"],
  "languages": {"de": "C2", "en": "B2"}
}
```

### PDF Output

Professional Swiss CV layout with:
- Contact information
- Professional summary
- Work experience (reverse chronological)
- Education
- Skills and competencies
- Languages
- Clean, professional formatting

## 🎨 Supported Languages

- **Deutsch** (German) - `--language de`
- **Français** (French) - `--language fr`
- **Italiano** (Italian) - `--language it`

Content is generated in the specified language with authentic Swiss context.

## 🏗️ Architecture

```
swiss-cv-generator/
├── src/
│   └── swiss_cv_generator/
│       ├── cli/              # Command-line interface
│       ├── data/             # Data models and loaders
│       ├── generation/       # OpenAI integration & sampling
│       ├── personas/         # Persona construction
│       └── export/           # JSON/PDF export
├── data/                     # Swiss demographic data
│   ├── cantons.json         # Canton info & population
│   ├── companies.json       # Swiss companies
│   ├── occupations.json     # Job titles
│   └── names_*.csv          # Names by language
├── templates/               # CV templates
├── tests/                   # Test suite
└── main.py                  # Entry point
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test category
pytest tests/unit -v
pytest tests/integration -v
```

Target: ≥90% code coverage

## 📊 Data Sources

- **BFS** (Federal Statistical Office): Canton demographics and population statistics
- **SBFI**: Swiss occupation classifications (CH-ISCO-19)
- **berufsberatung.ch**: Occupation data and career information
- **Zefix**: Swiss company registry

## ⚙️ Configuration

Edit `.env` to customize:

```bash
# OpenAI settings
OPENAI_API_KEY=sk-...          # Your OpenAI API key
OPENAI_MODEL=gpt-4o-mini       # Model (default)
OPENAI_MAX_TOKENS=500          # Max tokens
OPENAI_TEMPERATURE=0.7         # Creativity (0-2)

# Application settings
DEFAULT_LANGUAGE=de             # Default language
LOG_LEVEL=INFO                  # Logging level
MAX_RETRY_ATTEMPTS=3            # Retry attempts
```

## 🚨 Troubleshooting

### "ModuleNotFoundError"
```bash
# Ensure venv is activated
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### "OpenAI API key not found"
```bash
# Set environment variable
$env:OPENAI_API_KEY = "sk-..."
# Or create .env file (see Configuration)
```

### "Data files missing"
```bash
# Validate setup
python -m src.cli.main validate
# Check data/ folder exists and has required JSON/CSV files
```

### "PDF generation fails"
```bash
# Ensure WeasyPrint is installed
pip install weasyprint
```

## 📝 License

MIT License - See LICENSE file

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Submit pull request

## 📞 Support

- **Issues**: Report bugs on GitHub
- **Discussions**: Ask questions in Discussions
- **Documentation**: See docs/ folder

## 🎯 Roadmap

- [ ] Web UI for CV generation
- [ ] Batch processing API
- [ ] Custom company database
- [ ] Advanced filtering options
- [ ] Salary data integration
- [ ] LinkedIn profile export

## ⚠️ Disclaimer

This tool generates synthetic CVs for **testing, development, and research purposes only**. Do not use generated CVs for fraudulent purposes or to misrepresent real individuals.

---

**Made with ❤️ for the Swiss tech community** 🇨🇭

**Latest version**: 1.0.0 | **Updated**: October 2025
