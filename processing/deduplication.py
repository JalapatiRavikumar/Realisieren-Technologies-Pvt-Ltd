"""
Deduplication module for multi-source scraped records.

Computes source-aware, case-normalized deterministic keys to eliminate duplicate records
without cross-source collisions.
"""

from dataclasses import dataclass, field
import re
from typing import Sequence

from config import CONFIG
from models.record import ScrapedRecord


@dataclass
class DeduplicationResult:
    """Contains deduplicated records and summary metrics."""

    unique_records: list[ScrapedRecord] = field(default_factory=list)
    duplicate_records: list[ScrapedRecord] = field(default_factory=list)
    total_before: int = 0
    duplicates_detected: int = 0
    unique_count: int = 0


def _normalize_key_component(val: str | None) -> str:
    """
    Standardize a string field for deterministic hashing/key generation.
    Lowercase, strip leading/trailing whitespace, and collapse internal whitespace.
    """
    if not val:
        return ""
    val_str = str(val).strip().lower()
    return re.sub(r"\s+", " ", val_str)


def generate_duplicate_key(record: ScrapedRecord) -> str:
    """
    Construct a deterministic, source-aware deduplication key.

    Strategy:
        - Books: source | normalized_title | normalized_source_url
        - Quotes: source | normalized_quote_text | normalized_author
        - Fallback: source | normalized_name_or_title | normalized_source_url
    """
    norm_source = _normalize_key_component(record.source)
    norm_name = _normalize_key_component(record.name_or_title)
    norm_url = _normalize_key_component(record.source_url)
    norm_author = _normalize_key_component(record.author)

    if norm_source == _normalize_key_component(CONFIG.SOURCE_BOOKS):
        return f"{norm_source}|{norm_name}|{norm_url}"

    if norm_source == _normalize_key_component(CONFIG.SOURCE_QUOTES):
        return f"{norm_source}|{norm_name}|{norm_author}"

    return f"{norm_source}|{norm_name}|{norm_url}"


def deduplicate_records(
    records: Sequence[ScrapedRecord],
) -> DeduplicationResult:
    """
    Deduplicate an ordered sequence of ScrapedRecord instances.
    Preserves the first-seen instance and tracks duplicate statistics.

    Args:
        records: Collection of cleaned and validated ScrapedRecord objects.

    Returns:
        DeduplicationResult containing unique records and metrics.
    """
    seen_keys: set[str] = set()
    unique_records: list[ScrapedRecord] = []
    duplicate_records: list[ScrapedRecord] = []

    for record in records:
        key = generate_duplicate_key(record)
        if key in seen_keys:
            duplicate_records.append(record)
        else:
            seen_keys.add(key)
            unique_records.append(record)

    total_before = len(records)
    duplicates_count = len(duplicate_records)
    unique_count = len(unique_records)

    return DeduplicationResult(
        unique_records=unique_records,
        duplicate_records=duplicate_records,
        total_before=total_before,
        duplicates_detected=duplicates_count,
        unique_count=unique_count,
    )
