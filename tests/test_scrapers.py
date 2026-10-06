"""
Unit and integration tests for scrapers using deterministic mocked HTML fixtures.
"""

from unittest.mock import MagicMock, patch
import pytest
from bs4 import BeautifulSoup

from config import AppConfig
from scrapers.base_scraper import BaseScraper
from scrapers.books_scraper import BooksScraper
from scrapers.quotes_scraper import QuotesScraper

MOCK_BOOKS_PAGE_1 = """
<!DOCTYPE html>
<html>
<body>
    <ol class="row">
        <li class="col-xs-6 col-sm-4 col-md-3 col-lg-3">
            <article class="product_pod">
                <div class="image_container">
                    <a href="catalogue/a-light-in-the-attic_1000/index.html">
                        <img src="media/cache/thumb.jpg" alt="A Light in the Attic"/>
                    </a>
                </div>
                <p class="star-rating Three">
                    <i class="icon-star"></i>
                </p>
                <h3>
                    <a href="catalogue/a-light-in-the-attic_1000/index.html" title="A Light in the Attic">A Light in the ...</a>
                </h3>
                <div class="product_price">
                    <p class="price_color">£51.77</p>
                    <p class="instock availability">
                        <i class="icon-ok"></i> In stock
                    </p>
                </div>
            </article>
        </li>
    </ol>
    <ul class="pager">
        <li class="next"><a href="catalogue/page-2.html">next</a></li>
    </ul>
</body>
</html>
"""

MOCK_BOOKS_PAGE_2 = """
<!DOCTYPE html>
<html>
<body>
    <ol class="row">
        <li class="col-xs-6 col-sm-4 col-md-3 col-lg-3">
            <article class="product_pod">
                <p class="star-rating Five"></p>
                <h3>
                    <a href="tipping-the-velvet_999/index.html" title="Tipping the Velvet">Tipping the Velvet</a>
                </h3>
                <div class="product_price">
                    <p class="price_color">£53.74</p>
                    <p class="instock availability">In stock</p>
                </div>
            </article>
        </li>
    </ol>
    <ul class="pager">
        <!-- No next page here -->
    </ul>
</body>
</html>
"""

MOCK_QUOTES_PAGE_1 = """
<!DOCTYPE html>
<html>
<body>
    <div class="quote">
        <span class="text">“The world as we have created it is a process of our thinking.”</span>
        <span>by <small class="author">Albert Einstein</small>
            <a href="/author/Albert-Einstein">(about)</a>
        </span>
        <div class="tags">
            Tags:
            <a class="tag" href="/tag/change/">change</a>
            <a class="tag" href="/tag/thinking/">thinking</a>
        </div>
    </div>
    <ul class="pager">
        <li class="next"><a href="/page/2/">Next <span aria-hidden="true">&rarr;</span></a></li>
    </ul>
</body>
</html>
"""

MOCK_QUOTES_PAGE_2 = """
<!DOCTYPE html>
<html>
<body>
    <div class="quote">
        <span class="text">“It is our choices, Harry, that show what we truly are.”</span>
        <span>by <small class="author">J.K. Rowling</small>
            <a href="/author/J-K-Rowling">(about)</a>
        </span>
        <div class="tags">
            Tags:
            <a class="tag" href="/tag/choices/">choices</a>
        </div>
    </div>
    <ul class="pager">
        <!-- No next page -->
    </ul>
</body>
</html>
"""


class TestBooksScraperMocked:
    """Test BooksScraper parsing and dynamic pagination with mocked responses."""

    def test_extract_book_fields(self):
        scraper = BooksScraper(config=AppConfig())
        soup = BeautifulSoup(MOCK_BOOKS_PAGE_1, "html.parser")
        pod = soup.select_one("article.product_pod")

        record = scraper._extract_book_from_pod(
            pod, "https://books.toscrape.com/index.html", "2026-10-06T12:00:00Z"
        )

        assert record is not None
        assert record.name_or_title == "A Light in the Attic"
        assert record.source == "Books to Scrape"
        assert record.source_url == "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
        assert record.price == "£51.77"
        assert record.rating == "Three"
        assert record.availability == "In stock"

    def test_dynamic_pagination(self):
        scraper = BooksScraper(config=AppConfig())

        # Mock get_soup to return Page 1 on first call, Page 2 on second call
        soup_p1 = BeautifulSoup(MOCK_BOOKS_PAGE_1, "html.parser")
        soup_p2 = BeautifulSoup(MOCK_BOOKS_PAGE_2, "html.parser")

        with patch.object(scraper, "get_soup", side_effect=[soup_p1, soup_p2]) as mock_get_soup:
            records = scraper.scrape()

            assert len(records) == 2
            assert records[0].name_or_title == "A Light in the Attic"
            assert records[1].name_or_title == "Tipping the Velvet"
            assert mock_get_soup.call_count == 2


class TestQuotesScraperMocked:
    """Test QuotesScraper parsing and dynamic pagination with mocked responses."""

    def test_extract_quote_fields(self):
        scraper = QuotesScraper(config=AppConfig())
        soup = BeautifulSoup(MOCK_QUOTES_PAGE_1, "html.parser")
        block = soup.select_one("div.quote")

        record = scraper._extract_quote_from_block(
            block, "https://quotes.toscrape.com/", "2026-10-06T12:00:00Z"
        )

        assert record is not None
        assert "The world as we have created it" in record.name_or_title
        assert record.author == "Albert Einstein"
        assert record.tags == "change, thinking"
        assert record.source == "Quotes to Scrape"
        assert record.source_url == "https://quotes.toscrape.com/author/Albert-Einstein"

    def test_dynamic_pagination(self):
        scraper = QuotesScraper(config=AppConfig())

        soup_p1 = BeautifulSoup(MOCK_QUOTES_PAGE_1, "html.parser")
        soup_p2 = BeautifulSoup(MOCK_QUOTES_PAGE_2, "html.parser")

        with patch.object(scraper, "get_soup", side_effect=[soup_p1, soup_p2]) as mock_get_soup:
            records = scraper.scrape()

            assert len(records) == 2
            assert "The world as we have created it" in records[0].name_or_title
            assert "It is our choices, Harry" in records[1].name_or_title
            assert mock_get_soup.call_count == 2


class TestBaseScraperResilience:
    """Test BaseScraper retry and error handling."""

    def test_fetch_success(self):
        test_config = AppConfig(MAX_RETRIES=2, REQUEST_DELAY_SECONDS=0)
        scraper = BooksScraper(config=test_config)

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"<html><body>OK</body></html>"

        with patch.object(scraper.session, "get", return_value=mock_resp):
            resp = scraper.fetch("https://example.com")
            assert resp is not None
            assert resp.status_code == 200

    def test_fetch_retry_and_eventual_failure(self):
        test_config = AppConfig(MAX_RETRIES=2, BACKOFF_FACTOR=0.01, REQUEST_DELAY_SECONDS=0)
        scraper = BooksScraper(config=test_config)

        mock_resp = MagicMock()
        mock_resp.status_code = 500

        with patch.object(scraper.session, "get", return_value=mock_resp):
            resp = scraper.fetch("https://example.com/fail")
            assert resp is None
