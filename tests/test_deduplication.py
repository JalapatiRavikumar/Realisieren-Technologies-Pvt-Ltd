"""
Unit tests for deduplication module.
"""

from models.record import ScrapedRecord
from processing.deduplication import deduplicate_records, generate_duplicate_key


class TestDeduplication:
    """Test duplicate detection, key generation, and metrics tracking."""

    def test_exact_duplicates(self):
        rec1 = ScrapedRecord(
            source="Books to Scrape",
            source_url="https://books.toscrape.com/catalogue/book-1/index.html",
            name_or_title="A Light in the Attic",
            price=51.77,
        )
        rec2 = ScrapedRecord(
            source="Books to Scrape",
            source_url="https://books.toscrape.com/catalogue/book-1/index.html",
            name_or_title="A Light in the Attic",
            price=51.77,
        )

        res = deduplicate_records([rec1, rec2])
        assert res.total_before == 2
        assert res.duplicates_detected == 1
        assert res.unique_count == 1
        assert len(res.unique_records) == 1
        assert res.unique_records[0].name_or_title == "A Light in the Attic"

    def test_case_and_whitespace_differences(self):
        rec1 = ScrapedRecord(
            source="Quotes to Scrape",
            source_url="https://quotes.toscrape.com/author/einstein",
            name_or_title="Life is like riding a bicycle.",
            author="Albert Einstein",
        )
        rec2 = ScrapedRecord(
            source="Quotes to Scrape",
            source_url="https://quotes.toscrape.com/author/einstein",
            name_or_title="  life is like riding A BICYCLE.  ",
            author="albert einstein",
        )

        res = deduplicate_records([rec1, rec2])
        assert res.total_before == 2
        assert res.duplicates_detected == 1
        assert res.unique_count == 1

    def test_cross_source_records_remain_distinct(self):
        # A book and quote sharing the exact same title string must not collide
        rec_book = ScrapedRecord(
            source="Books to Scrape",
            source_url="https://books.toscrape.com/catalogue/common-title/index.html",
            name_or_title="To Kill a Mockingbird",
        )
        rec_quote = ScrapedRecord(
            source="Quotes to Scrape",
            source_url="https://quotes.toscrape.com/quote/1",
            name_or_title="To Kill a Mockingbird",
            author="Harper Lee",
        )

        res = deduplicate_records([rec_book, rec_quote])
        assert res.total_before == 2
        assert res.duplicates_detected == 0
        assert res.unique_count == 2
        assert len(res.unique_records) == 2

    def test_unique_records_preserved(self):
        records = [
            ScrapedRecord(
                source="Books to Scrape",
                source_url=f"https://books.toscrape.com/catalogue/book-{i}/index.html",
                name_or_title=f"Book Title {i}",
            )
            for i in range(10)
        ]

        res = deduplicate_records(records)
        assert res.total_before == 10
        assert res.duplicates_detected == 0
        assert res.unique_count == 10
        assert len(res.unique_records) == 10
