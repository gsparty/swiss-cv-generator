# Swiss CV Generator 🇨🇭

Generate realistic, culturally authentic Swiss CVs with authentic Swiss demographic data and AI-powered content generation.

## ✨ Features

- **Demographic Accuracy**: Population-weighted canton sampling with realistic age-to-experience correlations
- **Cultural Authenticity**: Language-appropriate names, Swiss contact patterns, industry-specific career progression
- **Multilingual**: Support for German (DE), French (FR), and Italian (IT)
- **Professional Output**: JSON and PDF exports with polished Swiss CV layouts
- **AI Integration**: AI-powered professional summaries with fallback templates
- **Flexible Filtering**: Generate CVs by canton, industry, language

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** (Python 3.13 recommended)
- **Git**
- **OpenAI API key** (optional - uses cached responses if unavailable)

### Installation

```powershell
# Clone repository
git clone https://github.com/gsparty/swiss-cv-generator.git
cd swiss-cv-generator

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1

# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browser
playwright install chromium
```

### Configuration (Optional)

```powershell
# Copy environment template
copy .env.example .env

# Edit .env and add your OpenAI API key (optional)
notepad .env
# Set: OPENAI_API_KEY=sk-...
```

### Generate Your First CV

```powershell
# Set PYTHONPATH (REQUIRED for every session)
$env:PYTHONPATH = "C:\Projects\swiss-cv-generator"  # Windows
# export PYTHONPATH="/path/to/swiss-cv-generator"    # macOS/Linux

# Generate 5 German CVs
python -m src.cli.main generate --count 5 --output-dir output

# Check output
ls output
```

---

## 📖 Usage Guide

### Basic Generation

```powershell
# IMPORTANT: Set PYTHONPATH first
$env:PYTHONPATH = "C:\Projects\swiss-cv-generator"

# Generate 5 CVs (default: German, both JSON+PDF)
python -m src.cli.main generate --count 5 --output-dir output

# Generate 10 CVs in French
python -m src.cli.main generate --count 10 --language fr --output-dir output

# Generate 3 CVs in Italian
python -m src.cli.main generate --count 3 --language it --output-dir output
```

### Filter by Canton

```powershell
# Generate 10 Zurich CVs
python -m src.cli.main generate --count 10 --canton ZH --output-dir zurich

# Generate 5 Geneva CVs
python -m src.cli.main generate --count 5 --canton GE --output-dir geneva

# Available cantons: ZH, BE, GE, BS, BL, AG, SO, LU, UR, SZ, OW, NW, GL, AR, AI, SG, TG, TI, VD, VS, NE, JU
```

### Filter by Industry

```powershell
# Generate tech CVs
python -m src.cli.main generate --count 10 --industry technology --output-dir tech

# Generate finance CVs
python -m src.cli.main generate --count 5 --industry finance --output-dir finance

# Available industries: technology, finance, healthcare, manufacturing, retail, 
# hospitality, education, construction, pharma, insurance, consulting, logistics
```

### Output Formats

```powershell
# JSON only
python -m src.cli.main generate --count 5 --format json --output-dir output

# PDF only
python -m src.cli.main generate --count 5 --format pdf --output-dir output

# Both (default)
python -m src.cli.main generate --count 5 --format both --output-dir output
```

### Validate Setup

```powershell
# Check that all data files are present
python -m src.cli.main validate
```

---

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
  "current_title": "Senior Technology Specialist",
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

---

## 🏗️ Project Structure

```
swiss-cv-generator/
├── src/
│   ├── cli/
│   │   └── main.py              # CLI entry point (Click-based)
│   ├── data/
│   │   ├── models.py            # Pydantic data models
│   │   ├── loader.py            # Swiss demographic data loaders
│   │   ├── cantons.json         # Canton population data
│   │   ├── companies.json       # Swiss companies by industry
│   │   ├── occupations.json     # CH-ISCO-19 job classifications
│   │   └── names_*.csv          # Name frequency lists
│   ├── generation/
│   │   ├── sampling.py          # Population-weighted sampling
│   │   ├── openai_client.py     # AI integration (optional)
│   │   └── prompts.py           # Multilingual templates
│   ├── personas/
│   │   └── persona_builder.py   # Persona orchestration
│   └── export/
│       ├── to_json.py           # JSON serialization
│       └── to_pdf.py            # PDF generation
├── output/                       # Generated CVs (default location)
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment template
└── README.md                     # This file
```

---

## ⚙️ Configuration

Edit `.env` to customize:

```bash
# OpenAI settings (optional - uses cached responses if not set)
OPENAI_API_KEY=sk-...           # Your OpenAI API key
OPENAI_MODEL=gpt-4o-mini        # Model to use
OPENAI_MAX_TOKENS=500           # Max tokens per request
OPENAI_TEMPERATURE=0.7          # Creativity (0-2)

# Application settings
DEFAULT_LANGUAGE=de             # Default language (de/fr/it)
LOG_LEVEL=INFO                  # Logging level
MAX_RETRY_ATTEMPTS=3            # Retry attempts for API calls
```

---

## 🚨 Troubleshooting

### "ModuleNotFoundError: No module named 'src'"

**Solution:** Set PYTHONPATH before running:
```powershell
# Windows PowerShell
$env:PYTHONPATH = "C:\Projects\swiss-cv-generator"

# macOS/Linux
export PYTHONPATH="/path/to/swiss-cv-generator"
```

### "ModuleNotFoundError: No module named 'click'"

**Solution:** Install dependencies:
```powershell
pip install -r requirements.txt
```

### "OpenAI API key not found"

**Solution:** The system uses cached responses by default. If you want fresh AI-generated content:
```powershell
# Set environment variable
$env:OPENAI_API_KEY = "sk-..."

# OR create .env file with your key
```

### "Data files missing"

**Solution:** Validate your setup:
```powershell
python -m src.cli.main validate
```

### PDF generation fails

**Solution:** Ensure Playwright is installed:
```powershell
playwright install chromium
```

---

## 📊 Data Sources

- **BFS (Federal Statistical Office)**: Canton demographics and population statistics
- **SBFI**: Swiss occupation classifications (CH-ISCO-19)
- **berufsberatung.ch**: Occupation data and career information
- **Zefix**: Swiss company registry
- **Swiss Name Statistics**: Census-based name frequency data

---

## 🎯 Common Commands Reference

```powershell
# Set PYTHONPATH (required every time)
$env:PYTHONPATH = "C:\Projects\swiss-cv-generator"

# Generate 5 CVs
python -m src.cli.main generate --count 5 --output-dir output

# Generate Zurich-only CVs
python -m src.cli.main generate --count 10 --canton ZH --output-dir zurich

# Generate tech CVs in French
python -m src.cli.main generate --count 5 --industry technology --language fr --output-dir tech_fr

# Validate setup
python -m src.cli.main validate

# Show help
python -m src.cli.main --help
python -m src.cli.main generate --help
```

---

## 🤝 Team Deployment Guide

**For teammates to run locally:**

1. **Clone the repository**
   ```powershell
   git clone https://github.com/gsparty/swiss-cv-generator.git
   cd swiss-cv-generator
   ```

2. **Set up virtual environment**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1  # Windows
   # source .venv/bin/activate    # macOS/Linux
   ```

3. **Install dependencies**
   ```powershell
   pip install -r requirements.txt
   playwright install chromium
   ```

4. **Set PYTHONPATH (CRITICAL)**
   ```powershell
   # Windows - adjust path to your location
   $env:PYTHONPATH = "C:\Users\YourName\Projects\swiss-cv-generator"
   
   # macOS/Linux
   export PYTHONPATH="/Users/yourname/projects/swiss-cv-generator"
   ```

5. **Generate test CVs**
   ```powershell
   python -m src.cli.main generate --count 3 --output-dir test
   ```

6. **Verify output**
   ```powershell
   ls test
   ```

**Note:** The PYTHONPATH must be set every time you open a new terminal. Add it to your profile for persistence.

---

## ⚠️ Disclaimer

This tool generates synthetic CVs for **testing, development, and research purposes only**. Do not use generated CVs for fraudulent purposes or to misrepresent real individuals.

---

## 📞 Support

- **Issues**: Report bugs on GitHub Issues
- **Questions**: Check existing issues or create a new one
- **Documentation**: See this README and code comments

---

**Made with ❤️ for the Swiss tech community** 🇨🇭

**Latest version**: 0.2.0 | **Updated**: November 2025