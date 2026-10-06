"""
Scraper service integrating the existing Python scraping pipeline with FastAPI.

Manages in-memory execution locking, dataset reads, search filtering,
and metrics aggregation from real output files.
"""

import csv
import json
import logging
from pathlib import Path
import sys
import threading
from typing import Any

# Ensure project root is in sys.path so pipeline, config, models can be imported
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from config import CONFIG
from pipeline.pipeline import Pipeline
from utils.logging_config import setup_logger

logger = setup_logger("ScraperService")

# In-memory execution state lock to prevent concurrent scraping jobs
_SCRAPER_LOCK = threading.Lock()
_IS_SCRAPER_RUNNING: bool = False


class ScraperService:
    """Service layer coordinating pipeline runs and file-backed data queries."""

    @staticmethod
    def is_running() -> bool:
        """Check if a scraping job is actively executing."""
        global _IS_SCRAPER_RUNNING
        return _IS_SCRAPER_RUNNING

    @classmethod
    def trigger_scrape(
        cls,
        source: str = "all",
        max_pages: int | None = None,
    ) -> dict[str, Any]:
        """
        Execute the scraping pipeline in a thread-safe manner.

        Args:
            source: 'all', 'books', or 'quotes'.
            max_pages: Optional maximum page limit.

        Returns:
            Dictionary with status and execution summary.
        """
        global _IS_SCRAPER_RUNNING

        # Acquire lock without blocking to check concurrency
        acquired = _SCRAPER_LOCK.acquire(blocking=False)
        if not acquired:
            return {
                "status": "running",
                "message": "Scraper is already running in another session.",
                "data": None,
            }

        _IS_SCRAPER_RUNNING = True
        try:
            logger.info(f"Triggering pipeline execution via API (source={source}, max_pages={max_pages})")
            pipeline = Pipeline(config=CONFIG)
            records, result = pipeline.run(source_filter=source, max_pages=max_pages)
            return {
                "status": "completed",
                "message": "Scraping completed successfully.",
                "data": result.to_summary_dict(),
            }
        except Exception as exc:
            logger.error(f"Error during API-triggered scrape: {exc}", exc_info=True)
            return {
                "status": "error",
                "message": "An internal error occurred during the scraping execution.",
                "data": None,
            }
        finally:
            _IS_SCRAPER_RUNNING = False
            _SCRAPER_LOCK.release()

    @staticmethod
    def get_summary_data() -> dict[str, Any] | None:
        """Read and parse output/summary_report.json."""
        summary_path = CONFIG.SUMMARY_JSON_PATH
        if not summary_path.exists():
            return None
        try:
            with open(summary_path, mode="r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as exc:
            logger.error(f"Error reading summary report JSON: {exc}")
            return None

    @classmethod
    def get_dashboard_stats(cls) -> dict[str, Any]:
        """
        Compute dashboard statistics from summary_report.json and final_dataset.csv.
        """
        summary = cls.get_summary_data()

        if summary:
            sources_data = summary.get("sources", {})
            books_stats = sources_data.get(CONFIG.SOURCE_BOOKS, {})
            quotes_stats = sources_data.get(CONFIG.SOURCE_QUOTES, {})

            return {
                "is_running": cls.is_running(),
                "total_records": summary.get("total_records_collected", 0),
                "books": books_stats.get("records_collected", 0),
                "quotes": quotes_stats.get("records_collected", 0),
                "valid_records": summary.get("total_records_after_cleaning", 0) - summary.get("total_records_rejected", 0),
                "rejected_records": summary.get("total_records_rejected", 0),
                "duplicates": summary.get("total_duplicates_detected", 0),
                "final_records": summary.get("final_record_count", 0),
                "last_run": summary.get("execution_finished_at"),
                "execution_time_seconds": summary.get("execution_time_seconds", 0.0),
                "sources_detail": {
                    "books": {
                        "name": CONFIG.SOURCE_BOOKS,
                        "status": "Completed" if not cls.is_running() else "Running",
                        "records_collected": books_stats.get("records_collected", 0),
                        "cleaned_records": books_stats.get("records_after_cleaning", 0),
                        "rejected_records": books_stats.get("records_rejected", 0),
                        "duplicates": books_stats.get("duplicates_detected", 0),
                    },
                    "quotes": {
                        "name": CONFIG.SOURCE_QUOTES,
                        "status": "Completed" if not cls.is_running() else "Running",
                        "records_collected": quotes_stats.get("records_collected", 0),
                        "cleaned_records": quotes_stats.get("records_after_cleaning", 0),
                        "rejected_records": quotes_stats.get("records_rejected", 0),
                        "duplicates": quotes_stats.get("duplicates_detected", 0),
                    },
                },
                "errors": summary.get("errors", []),
            }

        # Fallback if no scrape has occurred yet
        return {
            "is_running": cls.is_running(),
            "total_records": 0,
            "books": 0,
            "quotes": 0,
            "valid_records": 0,
            "rejected_records": 0,
            "duplicates": 0,
            "final_records": 0,
            "last_run": None,
            "execution_time_seconds": 0.0,
            "sources_detail": {
                "books": {
                    "name": CONFIG.SOURCE_BOOKS,
                    "status": "Pending",
                    "records_collected": 0,
                    "cleaned_records": 0,
                    "rejected_records": 0,
                    "duplicates": 0,
                },
                "quotes": {
                    "name": CONFIG.SOURCE_QUOTES,
                    "status": "Pending",
                    "records_collected": 0,
                    "cleaned_records": 0,
                    "rejected_records": 0,
                    "duplicates": 0,
                },
            },
            "errors": [],
        }

    @staticmethod
    def get_records(
        page: int = 1,
        limit: int = 20,
        source: str | None = None,
        search: str | None = None,
    ) -> dict[str, Any]:
        """
        Query and paginate records from final_dataset.csv with search and source filters.
        """
        csv_path = CONFIG.CSV_OUTPUT_PATH
        if not csv_path.exists():
            return {"records": [], "page": page, "limit": limit, "total": 0}

        all_records: list[dict[str, Any]] = []
        try:
            with open(csv_path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Clean empty strings into None for clean JSON response
                    record = {k: (v if v != "" else None) for k, v in row.items()}
                    all_records.append(record)
        except Exception as exc:
            logger.error(f"Error reading CSV records: {exc}")
            return {"records": [], "page": page, "limit": limit, "total": 0}

        # 1. Filter by source if specified
        filtered = all_records
        if source and source.strip().lower() not in ("all", ""):
            src_query = source.strip().lower()
            filtered = [
                r for r in filtered
                if r.get("source") and (
                    src_query in r["source"].lower() or
                    (src_query == "books" and "book" in r["source"].lower()) or
                    (src_query == "quotes" and "quote" in r["source"].lower())
                )
            ]

        # 2. Filter by search query across multiple textual fields
        if search and search.strip():
            query = search.strip().lower()
            search_fields = ["name_or_title", "author", "category", "tags", "description"]
            filtered = [
                r for r in filtered
                if any(r.get(field) and query in str(r[field]).lower() for field in search_fields)
            ]

        total_count = len(filtered)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_records = filtered[start_idx:end_idx]

        return {
            "records": paginated_records,
            "page": page,
            "limit": limit,
            "total": total_count,
            "total_pages": (total_count + limit - 1) // limit if limit > 0 else 1,
        }
