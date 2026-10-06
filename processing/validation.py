"""
Data validation module for scraped records.

Validates essential schema constraints, URL formats, numeric ranges,
and preserves detailed rejection reasons for QA reporting.
"""

from dataclasses import dataclass, field

from models.record import ScrapedRecord
from utils.http import is_valid_url


@dataclass
class ValidationResult:
    """Encapsulates the validation outcome and reasons for any failures."""

    is_valid: bool
    errors: list[str] = field(default_factory=list)

    def add_error(self, message: str) -> None:
        """Append an error message and set validity to False."""
        self.errors.append(message)
        self.is_valid = False


def validate_record(record: ScrapedRecord) -> ValidationResult:
    """
    Validate a ScrapedRecord against structural and domain rules.

    Required checks:
        - source exists and is non-empty string.
        - source_url exists and conforms to a valid HTTP/HTTPS URL.
        - name_or_title exists and is non-empty string.
        - price is numeric (float >= 0.0) when present.
        - rating is an integer between 1 and 5 when present.
        - optional fields missing (None) do NOT cause rejection.

    Args:
        record: ScrapedRecord instance to validate.

    Returns:
        ValidationResult containing pass/fail status and error list.
    """
    result = ValidationResult(is_valid=True)

    # 1. Structural check
    if not isinstance(record, ScrapedRecord):
        result.add_error(f"Invalid record type: expected ScrapedRecord, got {type(record).__name__}")
        return result

    # 2. Source validation
    if not record.source or not isinstance(record.source, str) or not record.source.strip():
        result.add_error("Missing or empty required field: 'source'")

    # 3. Source URL validation
    if not record.source_url or not isinstance(record.source_url, str) or not record.source_url.strip():
        result.add_error("Missing or empty required field: 'source_url'")
    elif not is_valid_url(record.source_url):
        result.add_error(f"Invalid 'source_url' format: {record.source_url!r}")

    # 4. Name or Title validation
    if not record.name_or_title or not isinstance(record.name_or_title, str) or not record.name_or_title.strip():
        result.add_error("Missing or empty required field: 'name_or_title'")

    # 5. Price validation (when present)
    if record.price is not None:
        if not isinstance(record.price, (int, float)):
            result.add_error(f"'price' must be a numeric value, got {type(record.price).__name__}: {record.price!r}")
        elif record.price < 0:
            result.add_error(f"'price' cannot be negative, got {record.price}")

    # 6. Rating validation (when present)
    if record.rating is not None:
        if not isinstance(record.rating, int) or isinstance(record.rating, bool):
            result.add_error(f"'rating' must be an integer, got {type(record.rating).__name__}: {record.rating!r}")
        elif not (1 <= record.rating <= 5):
            result.add_error(f"'rating' must be between 1 and 5, got {record.rating}")

    return result
