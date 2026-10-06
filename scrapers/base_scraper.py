"""
Reusable Base Scraper with resilient HTTP session management,
exponential backoff, polite request delay, and structured logging.
"""

from abc import ABC, abstractmethod
import logging
import time
from bs4 import BeautifulSoup
import requests
from requests.exceptions import HTTPError, RequestException, Timeout

from config import AppConfig, CONFIG
from models.record import ScrapedRecord
from utils.http import create_session, resolve_url
from utils.logging_config import setup_logger


class BaseScraper(ABC):
    """
    Abstract base scraper defining common network lifecycle,
    error resilience, and page parsing primitives.
    """

    def __init__(
        self,
        config: AppConfig = CONFIG,
        logger: logging.Logger | None = None,
    ) -> None:
        self.config = config
        self.logger = logger or setup_logger(self.__class__.__name__)
        self.session = create_session(
            user_agent=self.config.USER_AGENT,
            max_retries=self.config.MAX_RETRIES,
            backoff_factor=self.config.BACKOFF_FACTOR,
            status_forcelist=self.config.RETRY_STATUS_CODES,
        )

    def fetch(self, url: str) -> requests.Response | None:
        """
        Perform a resilient HTTP GET request with retries, timeouts, and error handling.

        Args:
            url: Target URL string to fetch.

        Returns:
            requests.Response object on success, or None on permanent failure.
        """
        retries = self.config.MAX_RETRIES
        delay = self.config.BACKOFF_FACTOR

        for attempt in range(1, retries + 1):
            try:
                self.logger.debug(f"Fetching URL (Attempt {attempt}/{retries}): {url}")
                response = self.session.get(
                    url,
                    timeout=self.config.REQUEST_TIMEOUT_SECONDS,
                )

                # Check for HTTP status errors (e.g., 404, 500)
                if response.status_code >= 400:
                    if response.status_code in self.config.RETRY_STATUS_CODES and attempt < retries:
                        self.logger.warning(
                            f"HTTP {response.status_code} received for {url}. "
                            f"Retrying in {delay:.1f}s (Attempt {attempt}/{retries})..."
                        )
                        time.sleep(delay)
                        delay *= 2
                        continue
                    else:
                        self.logger.error(
                            f"HTTP error {response.status_code} for URL: {url}"
                        )
                        return None

                # Polite delay between network operations
                if self.config.REQUEST_DELAY_SECONDS > 0:
                    time.sleep(self.config.REQUEST_DELAY_SECONDS)

                return response

            except Timeout:
                self.logger.warning(
                    f"Timeout fetching {url} (Attempt {attempt}/{retries})."
                )
                if attempt < retries:
                    time.sleep(delay)
                    delay *= 2
                else:
                    self.logger.error(f"Permanent timeout failure for {url}")
                    return None

            except RequestException as exc:
                self.logger.warning(
                    f"Network error on {url} (Attempt {attempt}/{retries}): {exc}"
                )
                if attempt < retries:
                    time.sleep(delay)
                    delay *= 2
                else:
                    self.logger.error(f"Permanent connection error for {url}: {exc}")
                    return None

            except Exception as exc:
                self.logger.error(f"Unexpected error fetching {url}: {exc}", exc_info=True)
                return None

        return None

    def get_soup(self, url: str) -> BeautifulSoup | None:
        """
        Fetch URL and return parsed BeautifulSoup DOM tree.

        Args:
            url: Target URL string.

        Returns:
            BeautifulSoup object on success, or None if network/parsing failed.
        """
        response = self.fetch(url)
        if response is None:
            return None
        try:
            return BeautifulSoup(response.content, "html.parser")
        except Exception as exc:
            self.logger.error(f"Failed to parse HTML from {url}: {exc}")
            return None

    def normalize_url(self, relative_url: str, base_url: str) -> str:
        """Normalize relative URLs to absolute paths."""
        return resolve_url(base_url, relative_url)

    def close(self) -> None:
        """Close underlying HTTP session connection pools."""
        if self.session:
            self.session.close()

    def __enter__(self) -> "BaseScraper":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    @abstractmethod
    def scrape(self, max_pages: int | None = None) -> list[ScrapedRecord]:
        """
        Execute scraping workflow for the concrete target source.

        Args:
            max_pages: Optional maximum page limit for testing or bounded runs.

        Returns:
            List of extracted ScrapedRecord objects.
        """
        raise NotImplementedError
