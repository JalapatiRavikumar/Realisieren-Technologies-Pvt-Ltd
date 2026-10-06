"""
FastAPI application entry point for the Multi-Source Web Scraping Backend.

Exposes REST APIs for dashboard metrics, paginated records, scraper execution,
and CSV/JSON file downloads.
"""

from pathlib import Path
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure root directory is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.routes.dashboard import router as dashboard_router
from backend.routes.records import router as records_router
from backend.routes.scraper import router as scraper_router

app = FastAPI(
    title="Multi-Source Web Scraping & Data Consolidation API",
    description="REST API backend exposing Python scraping pipeline and consolidated datasets.",
    version="1.0.0",
)

# CORS configuration for local React / Vite frontend development
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes with /api prefix
app.include_router(dashboard_router, prefix="/api")
app.include_router(records_router, prefix="/api")
app.include_router(scraper_router, prefix="/api")


@app.get("/api/health", tags=["Health"])
def health_check():
    """Health check endpoint to verify backend operational readiness."""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    print("Starting FastAPI Backend on http://localhost:8000 ...")
    uvicorn.run(app, host="127.0.0.1", port=8000)
