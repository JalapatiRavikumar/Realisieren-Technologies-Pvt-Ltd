# Multi-Source Web Scraping Frontend Dashboard

A modern, responsive React + Vite + Tailwind CSS dashboard that connects to the FastAPI backend and displays consolidated datasets, live pipeline execution controls, real-time statistics, and search/filter mechanisms.

---

## 1. Features

- **Executive Metrics Cards**: Real-time KPI cards for Total Raw Records, Books to Scrape count, Quotes to Scrape count, Valid records, Rejected records, Duplicates removed, and Final Dataset count.
- **Source Breakdown Panels**: Dedicated cards for *Books to Scrape* and *Quotes to Scrape* detailing collection status, cleaned records, rejections, and duplicate metrics.
- **Live Scraper Trigger**: Prominent **"Run Scraper"** button that sends requests to `POST /api/scrape`, prevents concurrent clicks, displays live status feedback, and automatically refreshes data upon completion.
- **Consolidated Data Table**:
  - Displays all 10 unified schema fields (`Source`, `Title/Quote`, `Category`, `Price`, `Rating`, `Author`, `Tags`, `Availability`, `Source URL`, `Scraped At`).
  - Truncated text with responsive layout.
  - "View Source" external links opening directly in a new tab.
  - Click-to-inspect modal panel ([RecordDetails.jsx](src/components/RecordDetails.jsx)).
- **Instant Search & Source Filter**:
  - Multi-field search across titles, quotes, authors, categories, and tags.
  - Source filter toggle (`All`, `Books to Scrape`, `Quotes to Scrape`).
  - Server-side / API pagination with configurable page size (10, 20, 50, 100).
- **One-Click File Downloads**: Direct download triggers for `final_dataset.csv` and `summary_report.json` served directly from the Python backend.
- **Resilient Error & Loading States**: Clean skeleton loaders and user-friendly error banners with automated connection health indicators.

---

## 2. Prerequisites

- **Node.js**: v18.0.0 or higher (v24.x recommended)
- **npm**: v9.0.0 or higher
- **FastAPI Backend**: Running concurrently on `http://localhost:8000`

---

## 3. Installation & Setup

### Step 1: Navigate to Frontend Directory
```bash
cd frontend
```

### Step 2: Install Dependencies
```bash
npm install
```

### Step 3: Configure Environment Variables (Optional)
Create a `.env` file in the `frontend/` directory (or rely on default `http://localhost:8000`):
```env
VITE_API_URL=http://localhost:8000
```

### Step 4: Start Vite Development Server
```bash
npm run dev
```

The frontend will be available at:
`http://localhost:5173`

---

## 4. Building for Production

To create an optimized production bundle:
```bash
npm run build
```
Output artifacts are generated in `frontend/dist/`.

---

## 5. Frontend Architecture & Directory Layout

```
frontend/
├── src/
│   ├── components/
│   │   ├── Navbar.jsx          # Top application bar with health indicators
│   │   ├── StatCard.jsx        # Summary KPI cards
│   │   ├── SourceCard.jsx      # Per-source extraction breakdown cards
│   │   ├── DataTable.jsx       # Consolidated table with pagination controls
│   │   ├── FilterBar.jsx       # Search input and source selector tabs
│   │   ├── RecordDetails.jsx   # Modal inspector for full record attributes
│   │   ├── LoadingState.jsx    # Animated spinner and skeleton loaders
│   │   └── ErrorMessage.jsx    # User-facing error notification banner
│   ├── pages/
│   │   └── Dashboard.jsx       # Main application page orchestrating data flow
│   ├── services/
│   │   └── api.js              # Centralized Axios client for FastAPI endpoints
│   ├── App.jsx                 # Root React component
│   ├── main.jsx                # Application mounting entry point
│   └── index.css               # Tailwind CSS directives & global scrollbar styles
├── package.json                # Frontend package manifest
├── vite.config.js              # Vite server & build configuration
├── tailwind.config.js          # Tailwind CSS theme configuration
└── README.md                   # Frontend documentation
```
