"""
HTTP session utilities, retry strategies, and URL helper functions.
"""

from urllib.parse import urljoin, urlparse
import requests
from urllib3.util import Retry
from requests.adapters import HTTPAdapter


def create_session(
    user_agent: str,
    max_retries: int = 3,
    backoff_factor: float = 1.5,
    status_forcelist: tuple[int, ...] = (429, 500, 502, 503, 504),
) -> requests.Session:
    """
    Build and configure a robust requests.Session with built-in retry logic.

    Args:
        user_agent: Custom User-Agent header string.
        max_retries: Maximum number of retry attempts for transient failures.
        backoff_factor: Backoff factor for exponential wait between retries.
        status_forcelist: HTTP status codes to trigger a retry on.

    Returns:
        Configured requests.Session object.
    """
    session = requests.Session()
    session.headers.update({
        "User-Agent": user_agent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    })

    retry_strategy = Retry(
        total=max_retries,
        backoff_factor=backoff_factor,
        status_forcelist=list(status_forcelist),
        allowed_methods=["HEAD", "GET", "OPTIONS"],
        raise_on_status=False,
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session


def resolve_url(base_url: str, relative_url: str) -> str:
    """
    Join and normalize a base URL and a relative link.

    Args:
        base_url: Current page URL or website base.
        relative_url: Target relative or absolute URL path.

    Returns:
        Absolute normalized URL string.
    """
    if not relative_url:
        return base_url
    return urljoin(base_url, relative_url.strip())


def is_valid_url(url: str | None) -> bool:
    """
    Check if a given string represents a valid HTTP/HTTPS URL.

    Args:
        url: URL string to validate.

    Returns:
        True if valid URL with scheme and network location, False otherwise.
    """
    if not url or not isinstance(url, str):
        return False
    try:
        parsed = urlparse(url.strip())
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False
