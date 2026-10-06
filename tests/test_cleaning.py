"""
Unit tests for data cleaning and normalization functions.
"""

import pytest
from models.record import ScrapedRecord
from processing.cleaning import (
    clean_record,
    clean_text,
    normalize_missing_value,
    normalize_tags,
    normalize_url,
    normalize_whitespace,
    parse_price,
    parse_rating,
)


class TestCleaningFunctions:
    """Test individual cleaning primitives."""

    @pytest.mark.parametrize(
        "input_val, expected",
        [
            ("   Hello    World   ", "Hello World"),
            ("\n\t  Line 1 \n Line 2 \t\t", "Line 1 Line 2"),
            ("NoExtraSpace", "NoExtraSpace"),
            ("", None),
            ("   ", None),
            (None, None),
        ],
    )
    def test_normalize_whitespace(self, input_val, expected):
        assert normalize_whitespace(input_val) == expected

    @pytest.mark.parametrize(
        "input_val, expected",
        [
            ("  A Light in the Attic  ", "A Light in the Attic"),
            ("Zero\u200bWidth\ufeffSpace", "ZeroWidthSpace"),
            ("   ", None),
            (None, None),
        ],
    )
    def test_clean_text(self, input_val, expected):
        assert clean_text(input_val) == expected

    @pytest.mark.parametrize(
        "input_val, expected",
        [
            ("N/A", None),
            ("n/a", None),
            ("NA", None),
            ("unknown", None),
            ("-", None),
            ("--", None),
            ("not available", None),
            ("none", None),
            ("null", None),
            ("", None),
            ("Valid Value", "Valid Value"),
            (42, 42),
            (None, None),
        ],
    )
    def test_normalize_missing_value(self, input_val, expected):
        assert normalize_missing_value(input_val) == expected

    @pytest.mark.parametrize(
        "url, base_url, expected",
        [
            ("catalogue/page-2.html", "https://books.toscrape.com/index.html", "https://books.toscrape.com/catalogue/page-2.html"),
            ("page-3.html", "https://books.toscrape.com/catalogue/page-2.html", "https://books.toscrape.com/catalogue/page-3.html"),
            ("https://books.toscrape.com/item.html", "https://books.toscrape.com/", "https://books.toscrape.com/item.html"),
            ("/author/Albert-Einstein", "https://quotes.toscrape.com/page/1/", "https://quotes.toscrape.com/author/Albert-Einstein"),
            ("", "https://example.com", None),
            ("   ", "https://example.com", None),
            (None, "https://example.com", None),
        ],
    )
    def test_normalize_url(self, url, base_url, expected):
        assert normalize_url(url, base_url) == expected

    @pytest.mark.parametrize(
        "input_val, expected",
        [
            ("£51.77", 51.77),
            ("Â£51.77", 51.77),
            ("$19.99", 19.99),
            ("€ 100.50", 100.50),
            ("51.77", 51.77),
            (51.77, 51.77),
            (25, 25.0),
            ("Free", None),
            ("N/A", None),
            (None, None),
        ],
    )
    def test_parse_price(self, input_val, expected):
        assert parse_price(input_val) == expected

    @pytest.mark.parametrize(
        "input_val, expected",
        [
            ("One", 1),
            ("Two", 2),
            ("Three", 3),
            ("Four", 4),
            ("Five", 5),
            ("one", 1),
            ("FIVE", 5),
            ("3", 3),
            (4, 4),
            (5.0, 5),
            ("Six", None),
            (0, None),
            (6, None),
            ("invalid", None),
            (None, None),
        ],
    )
    def test_parse_rating(self, input_val, expected):
        assert parse_rating(input_val) == expected

    @pytest.mark.parametrize(
        "input_val, expected",
        [
            (["change", "deep-thoughts", "thinking"], "change, deep-thoughts, thinking"),
            (["tag1", "tag1", "tag2"], "tag1, tag2"),
            ("change, deep-thoughts", "change, deep-thoughts"),
            ("   tagA ,   tagB  ", "tagA, tagB"),
            ([], None),
            ("", None),
            ("N/A", None),
            (None, None),
        ],
    )
    def test_normalize_tags(self, input_val, expected):
        assert normalize_tags(input_val) == expected

    def test_clean_record_full(self):
        raw = ScrapedRecord(
            source="  Books to Scrape  ",
            source_url="catalogue/a-light_1000/index.html",
            name_or_title="  A Light in the Attic  \n",
            category="  Poetry  ",
            price="£51.77",
            rating="Three",
            author="N/A",
            tags="n/a",
            description="  A nice book.\n\nMore info.  ",
            availability="  In stock (22 available)  ",
            scraped_at="2026-10-06T12:00:00Z",
        )

        cleaned = clean_record(raw)

        assert cleaned.source == "Books to Scrape"
        assert cleaned.source_url == "catalogue/a-light_1000/index.html"
        assert cleaned.name_or_title == "A Light in the Attic"
        assert cleaned.category == "Poetry"
        assert cleaned.price == 51.77
        assert cleaned.rating == 3
        assert cleaned.author is None
        assert cleaned.tags is None
        assert cleaned.description == "A nice book. More info."
        assert cleaned.availability == "In stock (22 available)"
