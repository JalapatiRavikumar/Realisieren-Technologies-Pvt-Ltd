"""Data processing package containing cleaning, validation, and deduplication modules."""

from processing.cleaning import clean_record
from processing.deduplication import deduplicate_records
from processing.validation import validate_record, ValidationResult

__all__ = [
    "clean_record",
    "deduplicate_records",
    "validate_record",
    "ValidationResult",
]
