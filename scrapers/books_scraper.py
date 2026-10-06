"""
Books to Scrape Web Scraper implementation.

Extracts book catalog items with dynamic next-page pagination,
polite request pacing, and resilient element extraction.
"""

from bs4 import BeautifulSoup, Tag

from config import AppConfig, CONFIG
from models.record import ScrapedRecord
from scrapers.base_scraper import BaseScraper
from utils.helpers import get_current_timestamp
from utils.http import resolve_url


class BooksScraper(BaseScraper):
    """Scraper implementation for https://books.toscrape.com/."""

    def __init__(self, config: AppConfig = CONFIG) -> None:
        super().__init__(config=config)
        self.source_name = self.config.SOURCE_BOOKS
        self.start_url = self.config.BOOKS_START_URL

    def _extract_book_from_pod(
        self,
        pod: Tag,
        page_url: str,
        timestamp: str,
    ) -> ScrapedRecord | None:
        """
        Extract book fields from a single product_pod HTML element.

        Args:
            pod: BeautifulSoup Tag for <article class="product_pod">.
            page_url: Current catalog page URL for resolving relative links.
            timestamp: ISO 8601 timestamp string.

        Returns:
            Populated ScrapedRecord or None if fundamental fields missing.
        """
        # 1. Title and Product Link
        title_tag = pod.select_one("h3 a")
        if not title_tag:
            return None

        title = title_tag.get("title") or title_tag.get_text(strip=True)
        raw_href = title_tag.get("href", "")
        product_url = resolve_url(page_url, raw_href)

        # 2. Price
        price_tag = pod.select_one("p.price_color")
        price_raw = price_tag.get_text(strip=True) if price_tag else None

        # 3. Availability
        avail_tag = pod.select_one("p.availability")
        availability = avail_tag.get_text(strip=True) if avail_tag else None

        # 4. Rating
        rating_tag = pod.select_one("p.star-rating")
        rating_raw = None
        if rating_tag:
            classes = rating_tag.get("class", [])
            # e.g., ['star-rating', 'Three'] -> 'Three'
            for cls in classes:
                if cls.lower() != "star-rating":
                    rating_raw = cls
                    break

        # 5. Optional details (Category & Description from detail page if enabled)
        category = None
        description = None
        if self.config.FETCH_BOOK_DETAILS and product_url:
            detail_soup = self.get_soup(product_url)
            if detail_soup:
                # Category is typically 3rd item in breadcrumb (Home > Books > Category)
                breadcrumb_links = detail_soup.select("ul.breadcrumb li a")
                if len(breadcrumb_links) >= 3:
                    category = breadcrumb_links[2].get_text(strip=True)

                desc_tag = detail_soup.select_one("#product_description ~ p")
                if desc_tag:
                    description = desc_tag.get_text(strip=True)

        return ScrapedRecord(
            source=self.source_name,
            source_url=product_url,
            name_or_title=title,
            category=category,
            price=price_raw,  # Cleaned later by pipeline cleaner
            rating=rating_raw,  # Cleaned later by pipeline cleaner
            author=None,
            tags=None,
            description=description,
            availability=availability,
            scraped_at=timestamp,
        )

    def scrape(self, max_pages: int | None = None) -> list[ScrapedRecord]:
        """
        Dynamically paginate through Books to Scrape catalog until no next page exists.

        Args:
            max_pages: Optional upper limit on pages to visit (defaults to config).

        Returns:
            List of raw ScrapedRecord instances.
        """
        records: list[ScrapedRecord] = []
        current_url = self.start_url
        page_num = 1
        page_limit = max_pages or self.config.DEFAULT_MAX_PAGES

        self.logger.info(f"Starting Books scraping from: {self.start_url}")

        while current_url:
            self.logger.info(f"[Books] Scraping page {page_num}: {current_url}")
            soup = self.get_soup(current_url)
            if soup is None:
                self.logger.error(f"[Books] Failed to load page {page_num} ({current_url}). Halting pagination.")
                break

            timestamp = get_current_timestamp()
            product_pods = soup.select("article.product_pod")
            self.logger.info(f"[Books] Found {len(product_pods)} books on page {page_num}")

            for pod in product_pods:
                try:
                    record = self._extract_book_from_pod(pod, current_url, timestamp)
                    if record:
                        records.append(record)
                except Exception as exc:
                    self.logger.warning(f"[Books] Error extracting book pod: {exc}")

            if page_limit and page_num >= page_limit:
                self.logger.info(f"[Books] Reached page limit ({page_limit}). Stopping pagination.")
                break

            # Dynamic pagination: check for next page link
            next_link_tag = soup.select_one("li.next a")
            if next_link_tag and next_link_tag.get("href"):
                next_rel_url = next_link_tag.get("href")
                current_url = resolve_url(current_url, next_rel_url)
                page_num += 1
            else:
                self.logger.info(f"[Books] No next page link found. Finished all {page_num} pages.")
                break

        self.logger.info(f"[Books] Scraping complete. Total books extracted: {len(records)}")
        return records
