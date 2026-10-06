"""
Standardized Data Model for Multi-Source Scraped Records.

Represents items collected from Books to Scrape and Quotes to Scrape
using a unified dataclass structure without fabricating missing attributes.
"""

from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class ScrapedRecord:
    """
    Unified record representation for items extracted from diverse web sources.

    Books mapping:
        name_or_title: book title
        price: numeric float price (e.g. 51.77)
        rating: integer rating 1-5
        category: genre/category string
        author: None
        tags: None
        description: product description text or None
        availability: stock status string (e.g. 'In stock')
        source: 'Books to Scrape'
        source_url: detail/product page URL

    Quotes mapping:
        name_or_title: quote text
        author: author name
        tags: comma-separated tags string (e.g. 'change, deep-thoughts')
        price: None
        rating: None
        category: None
        description: None
        availability: None
        source: 'Quotes to Scrape'
        source_url: source page or quote URL
    """

    source: str
    source_url: str
    name_or_title: str
    category: str | None = None
    price: float | None = None
    rating: int | None = None
    author: str | None = None
    tags: str | None = None
    description: str | None = None
    availability: str | None = None
    scraped_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert dataclass instance to a clean Python dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ScrapedRecord":
        """Construct a ScrapedRecord from a dictionary with key filtering."""
        valid_keys = cls.__dataclass_fields__.keys()
        filtered = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered)
