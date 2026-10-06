"""
End-to-End Web Scraping and Data Consolidation Pipeline.

Orchestrates multi-source extraction, data sanitization, schema validation,
deterministic deduplication, CSV export, and execution metrics reporting.
"""

from dataclasses import dataclass, field
import logging
import time
from typing import Any

from config import AppConfig, CONFIG
from models.record import ScrapedRecord
from processing.cleaning import clean_record
from processing.deduplication import deduplicate_records
from processing.validation import validate_record
from scrapers.books_scraper import BooksScraper
from scrapers.quotes_scraper import QuotesScraper
from utils.helpers import get_current_timestamp, save_records_to_csv, save_summary_json
from utils.logging_config import setup_logger


@dataclass
class SourceMetrics:
    """Per-source metrics tracking across processing stages."""

    records_collected: int = 0
    records_after_cleaning: int = 0
    records_rejected: int = 0
    duplicates_detected: int = 0

    def to_dict(self) -> dict[str, int]:
        return {
            "records_collected": self.records_collected,
            "records_after_cleaning": self.records_after_cleaning,
            "records_rejected": self.records_rejected,
            "duplicates_detected": self.duplicates_detected,
        }


@dataclass
class PipelineResult:
    """Complete summary of the pipeline execution and calculated metrics."""

    execution_started_at: str
    execution_finished_at: str
    execution_time_seconds: float
    sources: dict[str, dict[str, int]]
    total_records_collected: int
    total_records_after_cleaning: int
    total_records_rejected: int
    total_duplicates_detected: int
    final_record_count: int
    errors: list[str] = field(default_factory=list)
    rejection_reasons: list[dict[str, Any]] = field(default_factory=list)

    def to_summary_dict(self) -> dict[str, Any]:
        """Convert metrics to the exact required JSON schema."""
        return {
            "execution_started_at": self.execution_started_at,
            "execution_finished_at": self.execution_finished_at,
            "execution_time_seconds": round(self.execution_time_seconds, 2),
            "sources": self.sources,
            "total_records_collected": self.total_records_collected,
            "total_records_after_cleaning": self.total_records_after_cleaning,
            "total_records_rejected": self.total_records_rejected,
            "total_duplicates_detected": self.total_duplicates_detected,
            "final_record_count": self.final_record_count,
            "errors": self.errors,
        }


class Pipeline:
    """
    Main pipeline coordinator for executing web scrapers and data transforms.
    """

    def __init__(
        self,
        config: AppConfig = CONFIG,
        logger: logging.Logger | None = None,
    ) -> None:
        self.config = config
        self.logger = logger or setup_logger("Pipeline")

    def run(
        self,
        source_filter: str = "all",
        max_pages: int | None = None,
    ) -> tuple[list[ScrapedRecord], PipelineResult]:
        """
        Execute the end-to-end extraction and processing pipeline.

        Args:
            source_filter: 'all', 'books', or 'quotes'.
            max_pages: Optional maximum page limit per source.

        Returns:
            Tuple of (final_unique_records, pipeline_result_metrics).
        """
        start_time_sec = time.time()
        start_timestamp = get_current_timestamp()
        self.logger.info(f"=== Scraping Pipeline Started at {start_timestamp} (Source: {source_filter}) ===")

        source_metrics: dict[str, SourceMetrics] = {
            self.config.SOURCE_BOOKS: SourceMetrics(),
            self.config.SOURCE_QUOTES: SourceMetrics(),
        }
        raw_records: list[ScrapedRecord] = []
        pipeline_errors: list[str] = []
        rejection_reasons: list[dict[str, Any]] = []

        # 1. Scrape Books to Scrape
        if source_filter in ("all", "books"):
            try:
                self.logger.info(f"Starting extraction for source: {self.config.SOURCE_BOOKS}")
                with BooksScraper(config=self.config) as scraper:
                    books = scraper.scrape(max_pages=max_pages)
                    raw_records.extend(books)
                    source_metrics[self.config.SOURCE_BOOKS].records_collected = len(books)
                    self.logger.info(f"Successfully collected {len(books)} raw records from {self.config.SOURCE_BOOKS}")
            except Exception as exc:
                err_msg = f"Error during Books scraping: {exc}"
                self.logger.error(err_msg, exc_info=True)
                pipeline_errors.append(err_msg)

        # 2. Scrape Quotes to Scrape
        if source_filter in ("all", "quotes"):
            try:
                self.logger.info(f"Starting extraction for source: {self.config.SOURCE_QUOTES}")
                with QuotesScraper(config=self.config) as scraper:
                    quotes = scraper.scrape(max_pages=max_pages)
                    raw_records.extend(quotes)
                    source_metrics[self.config.SOURCE_QUOTES].records_collected = len(quotes)
                    self.logger.info(f"Successfully collected {len(quotes)} raw records from {self.config.SOURCE_QUOTES}")
            except Exception as exc:
                err_msg = f"Error during Quotes scraping: {exc}"
                self.logger.error(err_msg, exc_info=True)
                pipeline_errors.append(err_msg)

        total_collected = len(raw_records)
        self.logger.info(f"Extraction phase finished. Total raw records collected across sources: {total_collected}")

        # 3. Cleaning phase
        self.logger.info("Starting Data Cleaning and Normalization phase...")
        cleaned_records: list[ScrapedRecord] = []
        for rec in raw_records:
            cleaned = clean_record(rec)
            cleaned_records.append(cleaned)
            if cleaned.source in source_metrics:
                source_metrics[cleaned.source].records_after_cleaning += 1

        total_after_cleaning = len(cleaned_records)
        self.logger.info(f"Cleaning complete. Records processed: {total_after_cleaning}")

        # 4. Validation phase
        self.logger.info("Starting Data Validation phase...")
        valid_records: list[ScrapedRecord] = []
        for rec in cleaned_records:
            val_res = validate_record(rec)
            if val_res.is_valid:
                valid_records.append(rec)
            else:
                if rec.source in source_metrics:
                    source_metrics[rec.source].records_rejected += 1
                self.logger.warning(
                    f"Record rejected [{rec.source}]: {rec.name_or_title[:40]!r} - Errors: {val_res.errors}"
                )
                rejection_reasons.append({
                    "source": rec.source,
                    "title_or_text": rec.name_or_title,
                    "url": rec.source_url,
                    "errors": val_res.errors,
                })

        total_valid = len(valid_records)
        total_rejected = len(rejection_reasons)
        self.logger.info(f"Validation complete. Valid records: {total_valid}, Rejected records: {total_rejected}")

        # 5. Deduplication phase
        self.logger.info("Starting Deduplication phase...")
        dedup_result = deduplicate_records(valid_records)
        final_records = dedup_result.unique_records
        total_duplicates = dedup_result.duplicates_detected

        # Update per-source duplicate metrics
        for dup in dedup_result.duplicate_records:
            if dup.source in source_metrics:
                source_metrics[dup.source].duplicates_detected += 1

        self.logger.info(
            f"Deduplication complete. Duplicates removed: {total_duplicates}, Final unique records: {len(final_records)}"
        )

        # 6. Export outputs (CSV & JSON)
        self.logger.info(f"Exporting consolidated dataset to CSV: {self.config.CSV_OUTPUT_PATH}")
        rows_written = save_records_to_csv(final_records, self.config.CSV_OUTPUT_PATH)
        self.logger.info(f"Wrote {rows_written} rows to CSV successfully.")

        end_time_sec = time.time()
        end_timestamp = get_current_timestamp()
        duration_sec = end_time_sec - start_time_sec

        result = PipelineResult(
            execution_started_at=start_timestamp,
            execution_finished_at=end_timestamp,
            execution_time_seconds=duration_sec,
            sources={k: v.to_dict() for k, v in source_metrics.items()},
            total_records_collected=total_collected,
            total_records_after_cleaning=total_after_cleaning,
            total_records_rejected=total_rejected,
            total_duplicates_detected=total_duplicates,
            final_record_count=len(final_records),
            errors=pipeline_errors,
            rejection_reasons=rejection_reasons,
        )

        self.logger.info(f"Exporting summary report to JSON: {self.config.SUMMARY_JSON_PATH}")
        save_summary_json(result.to_summary_dict(), self.config.SUMMARY_JSON_PATH)
        self.logger.info("=== Scraping Pipeline Completed Successfully ===")

        return final_records, result
