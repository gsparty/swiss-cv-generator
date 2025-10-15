# 🇨🇭 Swiss CV Generator — MVP

Generate realistic, culturally authentic Swiss CVs directly from the command line.

This MVP creates professional-looking PDFs and JSON persona data with **no external dependencies beyond Playwright**.  
It works out-of-the-box on any machine that can install Python + Playwright.

---

## 🚀 Quick Start

git clone https://github.com/gsparty/swiss-cv-generator.git  
cd swiss-cv-generator

create virtual environment and install dependencies  
python -m venv .venv  
.\.venv\Scripts\Activate.ps1  
pip install -e .[dev]

install browser engines for Playwright  
playwright install chromium

generate a few Swiss CVs (default canton mix)  
python -m swisscv.cli.generate --count 3 --outdir demo_out --pdf-engine playwright --pdf-scale 0.92

**Output:**

demo_out/  
├─ Anna_Meier_0.pdf  
├─ Anna_Meier_0.json  
├─ Lukas_Bianchi_1.pdf  
└─ Lukas_Bianchi_1.json

- Each .pdf is a one-page Swiss CV.  
- Each .json contains the sampled demographic and persona data.

---

## 🧠 CLI Options

| Flag | Description |
|------|-------------|
| --count | Number of CVs to generate |
| --outdir | Output directory |
| --canton | Force canton code (e.g. ZH, VD, TI) |
| --pdf-engine | Beluto, playwright, or weasyprint |
| --pdf-scale | Scale factor for rendering (e.g. 0.92 for slightly smaller text) |
| --one-page | Try to force one-page CVs (truncates long summaries, shrinks scale) |
| --summary-max-chars | Maximum character length of the profile summary |

**Example (Zurich canton, one-page layout):**  
python -m swisscv.cli.generate --count 5 --outdir demo_final --canton ZH --one-page --pdf-engine playwright --pdf-scale 0.92

---

## 🖋 Fonts

By default, the templates use system fonts (Arial, Segoe UI, sans-serif),  
so they work everywhere with no setup.

**Optionally**, for consistent embedded typography:

mkdir templates\pdf\fonts  
Invoke-WebRequest https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans.ttf -OutFile templates\pdf\fonts\DejaVuSans.ttf

Then update 	emplates/pdf/de.html to reference DejaVuSans.ttf (already supported).

---

## 🗜 Optional PDF Compression

The generated PDFs are already small (~80–90 KB).  
If you'd like to compress them further, install Ghostscript and run:

.\compress-pdfs.ps1 -PdfDir .\demo_final

The script auto-detects Ghostscript if available and creates  
*_compressed.pdf versions in the same folder.

---

## ✅ Development Notes

- Uses **Playwright** for rendering (cross-platform, high-fidelity)  
- Uses **Jinja2** templates for layout and dynamic data  
- Generates both .pdf (visual CV) and .json (structured data)  
- No API keys or external services required for the demo

---

## 🧩 Roadmap (Post-MVP)

- Canton-specific datasets (names, cities, industries)  
- Optional OpenAI integration for summaries  
- Multilingual templates (fr, it, en)  
- Enhanced PDF design and branding presets  
- Deterministic persona sampling with tests + CI

---

**Author:** gsparty  
**License:** MIT
