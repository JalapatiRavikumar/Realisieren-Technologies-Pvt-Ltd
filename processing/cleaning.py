"""
Data cleaning and normalization utilities for raw scraped records.

Provides standardized sanitizers for text, prices, ratings, URLs, tags,
and missing value sentinels.
"""

import re
from typing import Any, Sequence
from urllib.parse import urljoin

from models.record import ScrapedRecord

# Missing value sentinel tokens mapped to None
MISSING_SENTINELS: frozenset[str] = frozenset({
    "",
    "n/a",
    "na",
    "null",
    "none",
    "unknown",
    "-",
    "--",
    "not available",
    "not applicable",
    "undefined",
})

# Word to integer mapping for star ratings
RATING_WORD_MAP: dict[str, int] = {
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
}


def normalize_whitespace(val: str | None) -> str | None:
    """
    Replace consecutive whitespace characters (newlines, tabs, spaces) with a single space.
    Trims leading and trailing whitespace.
    """
    if val is None:
        return None
    val_str = str(val).strip()
    if not val_str:
        return None
    return re.sub(r"\s+", " ", val_str)


def clean_text(val: str | None) -> str | None:
    """
    Clean and normalize generic text fields.

    Removes zero-width characters, collapses whitespace, and returns None if empty.
    """
    if val is None:
        return None
    cleaned = normalize_whitespace(val)
    if cleaned is None:
        return None
    # Strip lingering zero-width spaces or control chars
    cleaned = re.sub(r"[\u200b\u200c\u200d\ufeff]", "", cleaned).strip()
    return cleaned if cleaned else None


def normalize_missing_value(val: Any) -> Any:
    """
    Standardize sentinel values (e.g., 'N/A', 'unknown', '-') to None.
    """
    if val is None:
        return None
    if isinstance(val, str):
        cleaned = val.strip().lower()
        if cleaned in MISSING_SENTINELS:
            return None
    return val


def normalize_url(url: str | None, base_url: str | None = None) -> str | None:
    """
    Convert relative URLs to absolute URLs and strip whitespace.
    """
    if url is None:
        return None
    url_str = str(url).strip()
    if not url_str:
        return None
    if base_url:
        return urljoin(base_url.strip(), url_str)
    return url_str


def parse_price(val: Any) -> float | None:
    """
    Extract and convert currency strings (e.g., '£51.77', 'Â£51.77', '$12.99')
    into a clean float value.
    """
    val = normalize_missing_value(val)
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val)

    val_str = str(val).strip()
    # Match digits with optional decimal point
    match = re.search(r"(\d+(?:\.\d+)?)", val_str)
    if match:
        try:
            return round(float(match.group(1)), 2)
        except ValueError:
            return None
    return None


def parse_rating(val: Any) -> int | None:
    """
    Convert textual ('One', 'Two', 'Three', 'Four', 'Five') or numeric
    ratings into an integer between 1 and 5.
    """
    val = normalize_missing_value(val)
    if val is None:
        return None

    if isinstance(val, int):
        return val if 1 <= val <= 5 else None

    if isinstance(val, float):
        int_val = int(val)
        return int_val if 1 <= int_val <= 5 else None

    val_str = str(val).strip().lower()

    # Check word map
    if val_str in RATING_WORD_MAP:
        rating_num = RATING_WORD_MAP[val_str]
        return rating_num if 1 <= rating_num <= 5 else None

    # Check numeric digit strings
    match = re.search(r"\b([1-5])\b", val_str)
    if match:
        return int(match.group(1))

    return None


def normalize_tags(tags: Sequence[str] | str | None) -> str | None:
    """
    Normalize list of tags or tag string into a clean, comma-separated string.
    """
    tags = normalize_missing_value(tags)
    if tags is None:
        return None

    if isinstance(tags, str):
        raw_list = [t.strip() for t in tags.split(",") if t.strip()]
    elif isinstance(tags, (list, tuple, set)):
        raw_list = [str(t).strip() for t in tags if str(t).strip()]
    else:
        return None

    cleaned_list = []
    for item in raw_list:
        clean_item = clean_text(item)
        if clean_item and clean_item not in cleaned_list:
            cleaned_list.append(clean_item)

    if not cleaned_list:
        return None

    return ", ".join(cleaned_list)


def clean_record(record: ScrapedRecord) -> ScrapedRecord:
    """
    Apply all cleaning and normalization rules to a ScrapedRecord.
    Returns a new cleaned ScrapedRecord instance.
    """
    cleaned_source = clean_text(record.source) or record.source
    cleaned_source_url = normalize_url(record.source_url) or record.source_url
    cleaned_name = clean_text(record.name_or_title) or record.name_or_title

    cleaned_category = clean_text(normalize_missing_value(record.category))
    cleaned_price = parse_price(record.price)
    cleaned_rating = parse_rating(record.rating)
    cleaned_author = clean_text(normalize_missing_value(record.author))
    cleaned_tags = normalize_tags(record.tags)
    cleaned_description = clean_text(normalize_missing_value(record.description))
    cleaned_availability = clean_text(normalize_missing_value(record.availability))
    cleaned_scraped_at = clean_text(normalize_missing_value(record.scraped_at))

    return ScrapedRecord(
        source=cleaned_source,
        source_url=cleaned_source_url,
        name_or_title=cleaned_name,
        category=cleaned_category,
        price=cleaned_price,
        rating=cleaned_rating,
        author=cleaned_author,
        tags=cleaned_tags,
        description=cleaned_description,
        availability=cleaned_availability,
        scraped_at=cleaned_scraped_at,
    )
