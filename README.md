# Multi-Source Web Scraping & Data Consolidation Pipeline

An enterprise-grade, clean, and interview-ready full-stack solution featuring a **Python Web Scraping Pipeline**, a **FastAPI REST API**, and a **React (Vite + Tailwind CSS) Dashboard**.

---

## 1. System Architecture

```
┌────────────────────────────────────────────────────────┐
│             React Frontend (Vite + Tailwind)           │
│   Dashboard • Real-Time Stats • Search • Data Table    │
└───────────────────────────┬────────────────────────────┘
                            │ REST API (HTTP/JSON)
┌───────────────────────────▼────────────────────────────┐
│                    FastAPI Backend                     │
│  /api/dashboard • /api/records • /api/scrape • Download │
└───────────────────────────┬────────────────────────────┘
                            │ Service Invocation
┌───────────────────────────▼────────────────────────────┐
│                Python Scraping Pipeline                │
│    BooksScraper (50 pgs)    │    QuotesScraper (10 pgs) │
│                └──────────┬─┴──────────┘               │
│                           v                            │
│                  Standardized Model                    │
│                           v                            │
│                 Cleaning & Normalization               │
│                           v                            │
│                 Validation Quality Gate                │
│                           v                            │
│               Deterministic Deduplication              │
└───────────────────────────┬────────────────────────────┘
                            │ File I/O
┌───────────────────────────▼────────────────────────────┐
│                  Output / Single Truth                 │
│  output/final_dataset.csv   • output/summary_report.json│
│                      logs/scraper.log                  │
└────────────────────────────────────────────────────────┘
```

---

## 2. Project Layout

```
scraping_assignment/
├── backend/
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── dashboard.py     # /api/dashboard & /api/summary endpoints
│   │   ├── records.py       # /api/records pagination & search endpoint
│   │   └── scraper.py       # /api/scrape trigger & file download routes
│   ├── services/
│   │   └── scraper_service.py # In-memory lock & dataset query service
│   ├── main.py              # FastAPI app entry point with CORS
│   └── requirements.txt     # Backend dependencies
│
├── frontend/
│   ├── src/
│   │   ├── components/      # Navbar, StatCard, SourceCard, DataTable, FilterBar, etc.
│   │   ├── pages/           # Dashboard.jsx
│   │   ├── services/        # Centralized api.js client
│   │   ├── App.jsx & main.jsx
│   │   └── index.css        # Tailwind CSS styles
│   ├── package.json
│   ├── vite.config.js
│   └── README.md
│
├── scrapers/
│   ├── base_scraper.py      # Resilient base scraper with HTTP session & backoff
│   ├── books_scraper.py     # Books to Scrape extractor with dynamic pagination
│   └── quotes_scraper.py    # Quotes to Scrape extractor with dynamic pagination
│
├── models/
│   └── record.py            # Unified ScrapedRecord dataclass
│
├── processing/
│   ├── cleaning.py          # Data normalizers (price, rating, tags, missing values)
│   ├── validation.py        # Schema validation rules & rejection reasons
│   └── deduplication.py     # Deterministic source-aware deduplication
│
├── pipeline/
│   └── pipeline.py          # End-to-end orchestrator & audit metrics generator
│
├── utils/
│   ├── http.py              # Session factory & URL validation
│   ├── helpers.py           # UTF-8 CSV exporter, JSON serializer
│   └── logging_config.py    # File & console logging setup
│
├── output/
│   ├── final_dataset.csv    # Consolidated dataset output (1,100 records)
│   └── summary_report.json  # Calculated execution summary
│
├── logs/
│   └── scraper.log          # Application log file
│
├── tests/
│   ├── test_cleaning.py     # 38 cleaning unit tests
│   ├── test_validation.py   # 9 validation unit tests
│   ├── test_deduplication.py# 4 deduplication unit tests
│   ├── test_scrapers.py     # Mocked DOM scraping tests
│   └── test_api.py          # FastAPI endpoint integration tests
│
├── main.py                  # Standalone CLI entry point
├── config.py                # Centralized configuration
├── requirements.txt         # Root dependencies
├── README.md                # Project documentation
├── AI_USAGE.md              # Transparent AI disclosure
├── INTERVIEW_NOTES.md       # Technical interview Q&A
└── .gitignore               # Standard ignore patterns
```

---

## 3. Quick Start Guide

### Step 1: Install Python Dependencies
```bash
# Optional: Create virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

### Step 2: Start the FastAPI Backend
```bash
uvicorn backend.main:app --reload --port 8000
```
Backend API will be available at:
- **API Base**: `http://localhost:8000`
- **Interactive Swagger Docs**: `http://localhost:8000/docs`

### Step 3: Start the React Frontend
Open a new terminal window:
```bash
cd frontend
npm install
npm run dev
```
Frontend Dashboard will be live at:
- **Web UI**: `http://localhost:5173`

---

## 4. Standalone CLI & Testing

You can also run the core Python scraper and tests completely independently of the frontend/API:

### Run Core Pipeline via CLI
```bash
python main.py
```

### Run Full Test Suite
```bash
pytest -v
```
*(Runs 90 unit, integration, and API tests completely offline in ~1 second)*

---

## 5. REST API Specifications

| Method | Endpoint | Description | Query / Body Params |
|---|---|---|---|
| `GET` | `/api/health` | Backend status check | None |
| `GET` | `/api/dashboard` | Dashboard metrics & source breakdown | None |
| `GET` | `/api/summary` | Full `summary_report.json` data | None |
| `GET` | `/api/records` | Paginated records from `final_dataset.csv` | `page=1`, `limit=20`, `source=all`, `search=einstein` |
| `POST` | `/api/scrape` | Trigger Python scraping pipeline | `{"source": "all", "max_pages": null}` |
| `GET` | `/api/download/csv` | Download generated `final_dataset.csv` | None |
| `GET` | `/api/download/summary` | Download generated `summary_report.json` | None |

---

## 6. Frontend Dashboard Features

1. **KPI Stat Cards**: Total records, Books count, Quotes count, Valid records, Rejected records, Duplicates removed, Final dataset size.
2. **Dedicated Source Cards**: Granular breakdown of collection progress, cleaning counts, and status for *Books to Scrape* and *Quotes to Scrape*.
3. **Execution Controls**: "Run Scraper" button triggering the backend pipeline with concurrency locking, loading animations, and automatic refresh.
4. **Interactive Data Table**: Search across multiple fields, source filtering tabs, pagination with configurable page size (10, 20, 50, 100), and click-to-view record details modal.
5. **Direct Downloads**: Direct CSV and JSON summary file downloads.
6. **Resilient Health State**: Live API connection indicator and user-friendly error recovery states.

---

## 7. Design Principles & Interview Readiness

- **Single Source of Truth**: The FastAPI API reads from the actual output files (`output/final_dataset.csv` and `output/summary_report.json`), avoiding duplicated or mocked data stores.
- **Defensive Concurrency**: In-memory job lock prevents concurrent scraping runs from overwhelming target sites or colliding during file writes.
- **Decoupled Architecture**: The core Python scraping pipeline remains 100% self-contained and runnable via `python main.py` even if the API or frontend is removed.

Refer to [INTERVIEW_NOTES.md](INTERVIEW_NOTES.md) for detailed oral interview answers on architecture, concurrency, deduplication, rate limiting, and scaling.
