"""
Centralized Configuration for Web Scraping Pipeline.

Contains all source URLs, HTTP timeouts, retry settings, request delays,
and directory/file output paths to avoid magic constants across the codebase.
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppConfig:
    """Immutable application configuration."""

    # Base Paths
    BASE_DIR: Path = Path(__file__).resolve().parent
    OUTPUT_DIR: Path = BASE_DIR / "output"
    LOGS_DIR: Path = BASE_DIR / "logs"

    # Output Files
    CSV_OUTPUT_PATH: Path = OUTPUT_DIR / "final_dataset.csv"
    SUMMARY_JSON_PATH: Path = OUTPUT_DIR / "summary_report.json"
    LOG_FILE_PATH: Path = LOGS_DIR / "scraper.log"

    # Scraping Targets
    BOOKS_START_URL: str = "https://books.toscrape.com/"
    QUOTES_START_URL: str = "https://quotes.toscrape.com/"

    # Source Identifier Names
    SOURCE_BOOKS: str = "Books to Scrape"
    SOURCE_QUOTES: str = "Quotes to Scrape"

    # HTTP Network Settings
    REQUEST_TIMEOUT_SECONDS: int = 15
    MAX_RETRIES: int = 3
    BACKOFF_FACTOR: float = 1.5
    RETRY_STATUS_CODES: tuple[int, ...] = (429, 500, 502, 503, 504)
    REQUEST_DELAY_SECONDS: float = 0.2  # Polite delay between requests
    USER_AGENT: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36 (InterviewAssignmentBot/1.0)"
    )

    # Optional Feature Flags
    # If True, BooksScraper visits each book detail page for description & category.
    # If False, BooksScraper extracts all available fields from catalog listings (faster).
    FETCH_BOOK_DETAILS: bool = False
    
    # Max pages to scrape per source (None = scrape until pagination ends)
    DEFAULT_MAX_PAGES: int | None = None


# Default global instance for convenience
CONFIG = AppConfig()
