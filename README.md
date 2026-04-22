# Lab Report Analyzer

AI-powered clinical lab report analysis for Dr. D. R. Gamalathge (MBBS, SLMC No. 36999).

Accepts uploaded PDFs, photos, or pasted lab text → runs Claude AI clinical analysis → generates a professional PDF report. Single-user, self-hosted, offline-capable PWA.

## Features

- Upload lab reports as PDF, image (JPG/PNG), or paste raw text
- Claude AI extracts and structures lab values (including via vision for photos)
- CVD risk: WHO SEAR-B model, 10-year, South Asian 1.4× calibration (NICE NG238 · ESC/EAS 2021)
- Clinical patterns, management suggestions (WHO/NICE/ESC — no RACGP), action plan
- Sri Lankan dietary/lifestyle guidance; Suwa Seriya 1990 emergency number in red flags
- Editable draft review before PDF generation
- Stately Editorial PDF: warm sand background, terracotta accents, 11 clinical sections
- Searchable report history with delete
- PWA — installable on mobile, works offline for history

## Quick Start

### Prerequisites

- Docker + Docker Compose
- An Anthropic API key

### 1. Clone and configure

```bash
git clone <repo-url>
cd Lab-report-analyzer-
cp .env.example .env
# Edit .env and set your ANTHROPIC_API_KEY
```

### 2. Start

```bash
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Health check: http://localhost:8000/api/health

### 3. Install as PWA (mobile)

Open http://localhost:3000 in Safari (iOS) or Chrome (Android) → Share → Add to Home Screen.

---

## Local Development (without Docker)

### Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env   # add ANTHROPIC_API_KEY
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install --legacy-peer-deps
cp .env.example .env.local   # NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

---

## API Reference

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/upload` | Upload PDF or image |
| POST | `/api/analyze/start` | Parse labs + run clinical analysis |
| POST | `/api/analyze/confirm` | Generate PDF report |
| GET | `/api/reports` | List reports (paginated) |
| GET | `/api/reports/{id}` | Report detail |
| GET | `/api/reports/{id}/pdf` | Download PDF |
| DELETE | `/api/reports/{id}` | Delete report |
| GET | `/api/health` | Health check |

---

## CVD Risk Model

Uses the **WHO CVD Risk Charts 2019 (SEAR-B)** — the South-East Asia Region B model covering Sri Lanka:

- 10-year absolute cardiovascular risk
- South Asian 1.4× calibration applied (Tillin 2013 · INTERHEART South Asia)
- NICE NG238 (2023) statin threshold: ≥10% → treatment recommended
- ESC/EAS 2021 risk categories: LOW / MODERATE / HIGH / VERY HIGH
- Clinical bypasses: known CVD, suspected FH, eGFR <30, LDL ≥4.9 mmol/L
- No Australian tools (no RACGP, no ACC-AHA Pooled Cohort Equations)

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14, TypeScript, Tailwind CSS, next-pwa |
| Backend | FastAPI, Python 3.11, SQLAlchemy async, SQLite |
| AI | Anthropic SDK, claude-sonnet-4-6, tool use |
| PDF | ReportLab (Stately Editorial design) |
| PDF reading | pdfplumber |
| Image reading | Claude Vision API |
| Container | Docker Compose |

---

## Data Storage

- Reports: `backend/lab_reports.db` (SQLite, gitignored)
- Generated PDFs: `backend/generated_reports/` (gitignored)
- Uploads: `backend/uploads/` (gitignored)

All data stays on your machine. Nothing is sent to external services except the lab text sent to the Anthropic API for analysis.

---

## Disclaimer

This tool is an interpretive aid for qualified clinicians. Risk calculations use the WHO SEAR-B CVD model with South Asian calibration (NICE NG238 · ESC/EAS 2021). It is not a replacement for clinical judgment.
