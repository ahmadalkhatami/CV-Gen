# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the development server (http://localhost:5000)
python app.py

# Windows shortcut (installs deps + opens browser)
run.bat
```

There are no tests, linting configs, or build steps.

## Architecture

Flask backend with a vanilla JS single-page frontend. All processing is stateless (no database, no sessions).

**Core data flow:**
```
LinkedIn input (ZIP/PDF/text) → Parser → Translator (if Indonesian) → JSON
→ User edits form → Collect cvData → ATS check → PDF/DOCX generation → Download
```

### Backend (`app.py`)

Seven API endpoints, all under `/api/`. Route handlers do lazy imports from `utils/` and return JSON. The `_check_ats_score` function scores CV data 0–100 by deducting points for missing or thin fields.

### Utils (`utils/`)

| File | Responsibility |
|---|---|
| `linkedin_parser.py` | Parse LinkedIn data export ZIP (CSV files) |
| `linkedin_text_parser.py` | Parse LinkedIn PDF saves or pasted profile text |
| `pdf_generator.py` | ReportLab-based PDF with 4 color themes |
| `docx_generator.py` | python-docx-based DOCX with matching themes |
| `translator.py` | Indonesian→English translation via deep-translator, with graceful fallback |

### Frontend (`static/js/app.js`, `templates/index.html`)

Single `cvData` object holds all CV state. Multi-step wizard (Import → Edit → Theme → Download). ATS score is also computed client-side for instant feedback.

**Themes:** Classic, Modern, Minimal, Executive — applied consistently across both PDF and DOCX generators.

## Key Behaviors

- **Bilingual parsing:** Section headers are detected in both English and Indonesian. Language is auto-detected by counting Indonesian marker words.
- **Translation protection:** Company names, school names, and URLs are intentionally NOT translated.
- **PDF extraction fallback chain:** pdfplumber → pypdf → PyPDF2 (graceful degradation).
- **Upload limit:** 32MB max.
- **Debug mode is on** in `app.py` — disable for production (`debug=False`).
