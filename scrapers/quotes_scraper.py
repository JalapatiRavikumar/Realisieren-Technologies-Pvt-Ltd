"""
Quotes to Scrape Web Scraper implementation.

Extracts quote records, authors, tags, and source URLs with dynamic next-page pagination.
"""

from bs4 import BeautifulSoup, Tag

from config import AppConfig, CONFIG
from models.record import ScrapedRecord
from scrapers.base_scraper import BaseScraper
from utils.helpers import get_current_timestamp
from utils.http import resolve_url


class QuotesScraper(BaseScraper):
    """Scraper implementation for https://quotes.toscrape.com/."""

    def __init__(self, config: AppConfig = CONFIG) -> None:
        super().__init__(config=config)
        self.source_name = self.config.SOURCE_QUOTES
        self.start_url = self.config.QUOTES_START_URL

    def _extract_quote_from_block(
        self,
        quote_tag: Tag,
        page_url: str,
        timestamp: str,
    ) -> ScrapedRecord | None:
        """
        Extract quote fields from a single div.quote HTML block.

        Args:
            quote_tag: BeautifulSoup Tag for <div class="quote">.
            page_url: Current page URL for relative resolution.
            timestamp: ISO 8601 timestamp string.

        Returns:
            Populated ScrapedRecord or None if fundamental fields missing.
        """
        # 1. Quote text
        text_tag = quote_tag.select_one("span.text")
        if not text_tag:
            return None
        quote_text = text_tag.get_text(strip=True)

        # 2. Author
        author_tag = quote_tag.select_one("small.author")
        author = author_tag.get_text(strip=True) if author_tag else None

        # 3. Tags
        tag_elements = quote_tag.select("div.tags a.tag")
        tags_list = [t.get_text(strip=True) for t in tag_elements if t.get_text(strip=True)]
        tags_str = ", ".join(tags_list) if tags_list else None

        # 4. Author detail URL / Quote source URL
        author_link_tag = quote_tag.select_one("a[href*='/author/']")
        if author_link_tag and author_link_tag.get("href"):
            source_url = resolve_url(page_url, author_link_tag.get("href"))
        else:
            source_url = page_url

        return ScrapedRecord(
            source=self.source_name,
            source_url=source_url,
            name_or_title=quote_text,
            category=None,
            price=None,
            rating=None,
            author=author,
            tags=tags_str,
            description=None,
            availability=None,
            scraped_at=timestamp,
        )

    def scrape(self, max_pages: int | None = None) -> list[ScrapedRecord]:
        """
        Dynamically paginate through Quotes to Scrape until no next page link exists.

        Args:
            max_pages: Optional upper limit on pages to scrape.

        Returns:
            List of raw ScrapedRecord instances.
        """
        records: list[ScrapedRecord] = []
        current_url = self.start_url
        page_num = 1
        page_limit = max_pages or self.config.DEFAULT_MAX_PAGES

        self.logger.info(f"Starting Quotes scraping from: {self.start_url}")

        while current_url:
            self.logger.info(f"[Quotes] Scraping page {page_num}: {current_url}")
            soup = self.get_soup(current_url)
            if soup is None:
                self.logger.error(f"[Quotes] Failed to load page {page_num} ({current_url}). Halting pagination.")
                break

            timestamp = get_current_timestamp()
            quote_blocks = soup.select("div.quote")
            self.logger.info(f"[Quotes] Found {len(quote_blocks)} quotes on page {page_num}")

            for block in quote_blocks:
                try:
                    record = self._extract_quote_from_block(block, current_url, timestamp)
                    if record:
                        records.append(record)
                except Exception as exc:
                    self.logger.warning(f"[Quotes] Error extracting quote block: {exc}")

            if page_limit and page_num >= page_limit:
                self.logger.info(f"[Quotes] Reached page limit ({page_limit}). Stopping pagination.")
                break

            # Dynamic pagination: check for next page link
            next_link_tag = soup.select_one("li.next a")
            if next_link_tag and next_link_tag.get("href"):
                next_rel_url = next_link_tag.get("href")
                current_url = resolve_url(current_url, next_rel_url)
                page_num += 1
            else:
                self.logger.info(f"[Quotes] No next page link found. Finished all {page_num} pages.")
                break

        self.logger.info(f"[Quotes] Scraping complete. Total quotes extracted: {len(records)}")
        return records
