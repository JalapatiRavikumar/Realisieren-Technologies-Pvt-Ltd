"""
File I/O, CSV export, and JSON serialization helpers for the pipeline.
"""

import csv
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Sequence

# Canonical field order for CSV output as specified in the assignment
CSV_FIELDNAMES = [
    "source",
    "source_url",
    "name_or_title",
    "category",
    "price",
    "rating",
    "author",
    "tags",
    "description",
    "availability",
    "scraped_at",
]


def get_current_timestamp() -> str:
    """Return current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()


def save_records_to_csv(records: Sequence[Any], file_path: Path) -> int:
    """
    Save list of records (dataclasses or dicts) to a UTF-8 encoded CSV file.

    Args:
        records: Collection of ScrapedRecord instances or dictionaries.
        file_path: Target CSV destination path.

    Returns:
        Number of rows written.
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)

    rows_written = 0
    with open(file_path, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=CSV_FIELDNAMES,
            extrasaction="ignore",
            quoting=csv.QUOTE_MINIMAL,
        )
        writer.writeheader()

        for rec in records:
            if hasattr(rec, "to_dict"):
                row = rec.to_dict()
            elif isinstance(rec, dict):
                row = rec
            else:
                row = rec.__dict__

            # Format None values as empty strings for clean CSV representation
            clean_row = {
                k: ("" if v is None else v)
                for k, v in row.items()
            }
            writer.writerow(clean_row)
            rows_written += 1

    return rows_written


def save_summary_json(data: dict[str, Any], file_path: Path) -> None:
    """
    Save summary metrics dictionary to an indented UTF-8 JSON file.

    Args:
        data: Metrics dictionary.
        file_path: Destination JSON path.
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, mode="w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
