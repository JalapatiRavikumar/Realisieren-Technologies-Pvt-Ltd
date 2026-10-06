"""
Unit tests for data validation module.
"""

import pytest
from models.record import ScrapedRecord
from processing.validation import validate_record


class TestValidation:
    """Test validation rules and rejection reasons."""

    def test_valid_book_record(self):
        record = ScrapedRecord(
            source="Books to Scrape",
            source_url="https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
            name_or_title="A Light in the Attic",
            category="Poetry",
            price=51.77,
            rating=3,
            author=None,
            tags=None,
            description="Classic poetry collection.",
            availability="In stock",
            scraped_at="2026-10-06T12:00:00Z",
        )
        res = validate_record(record)
        assert res.is_valid is True
        assert len(res.errors) == 0

    def test_valid_quote_record(self):
        record = ScrapedRecord(
            source="Quotes to Scrape",
            source_url="https://quotes.toscrape.com/author/Albert-Einstein",
            name_or_title="The world as we have created it is a process of our thinking.",
            author="Albert Einstein",
            tags="change, deep-thoughts, thinking, world",
            price=None,
            rating=None,
            category=None,
            description=None,
            availability=None,
            scraped_at="2026-10-06T12:00:00Z",
        )
        res = validate_record(record)
        assert res.is_valid is True
        assert len(res.errors) == 0

    def test_missing_source(self):
        record = ScrapedRecord(
            source="",
            source_url="https://books.toscrape.com/item.html",
            name_or_title="Test Book",
        )
        res = validate_record(record)
        assert res.is_valid is False
        assert any("source" in err for err in res.errors)

    def test_missing_source_url(self):
        record = ScrapedRecord(
            source="Books to Scrape",
            source_url="",
            name_or_title="Test Book",
        )
        res = validate_record(record)
        assert res.is_valid is False
        assert any("source_url" in err for err in res.errors)

    def test_invalid_source_url_format(self):
        record = ScrapedRecord(
            source="Books to Scrape",
            source_url="not-a-valid-url",
            name_or_title="Test Book",
        )
        res = validate_record(record)
        assert res.is_valid is False
        assert any("format" in err for err in res.errors)

    def test_missing_name_or_title(self):
        record = ScrapedRecord(
            source="Books to Scrape",
            source_url="https://books.toscrape.com/item.html",
            name_or_title="   ",
        )
        res = validate_record(record)
        assert res.is_valid is False
        assert any("name_or_title" in err for err in res.errors)

    def test_invalid_negative_price(self):
        record = ScrapedRecord(
            source="Books to Scrape",
            source_url="https://books.toscrape.com/item.html",
            name_or_title="Test Book",
            price=-10.5,
        )
        res = validate_record(record)
        assert res.is_valid is False
        assert any("negative" in err for err in res.errors)

    def test_invalid_rating_range(self):
        record_low = ScrapedRecord(
            source="Books to Scrape",
            source_url="https://books.toscrape.com/item.html",
            name_or_title="Test Book",
            rating=0,
        )
        res_low = validate_record(record_low)
        assert res_low.is_valid is False
        assert any("rating" in err for err in res_low.errors)

        record_high = ScrapedRecord(
            source="Books to Scrape",
            source_url="https://books.toscrape.com/item.html",
            name_or_title="Test Book",
            rating=6,
        )
        res_high = validate_record(record_high)
        assert res_high.is_valid is False
        assert any("rating" in err for err in res_high.errors)

    def test_optional_fields_as_none_should_pass(self):
        record = ScrapedRecord(
            source="Quotes to Scrape",
            source_url="https://quotes.toscrape.com/page/1/",
            name_or_title="Sample quote text",
            category=None,
            price=None,
            rating=None,
            author=None,
            tags=None,
            description=None,
            availability=None,
        )
        res = validate_record(record)
        assert res.is_valid is True
