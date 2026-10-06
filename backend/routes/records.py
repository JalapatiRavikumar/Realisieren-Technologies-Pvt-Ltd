"""
Records query endpoint with pagination, source filter, and multi-field search.
"""

from fastapi import APIRouter, Query
from backend.services.scraper_service import ScraperService

router = APIRouter(tags=["Records"])


@router.get("/records")
def list_records(
    page: int = Query(default=1, ge=1, description="Page number"),
    limit: int = Query(default=20, ge=1, le=100, description="Records per page"),
    source: str | None = Query(default=None, description="Filter by source (all, books, quotes)"),
    search: str | None = Query(default=None, description="Search term across title, author, tags, category"),
):
    """
    Retrieve paginated records from output/final_dataset.csv with search and source filtering.
    """
    return ScraperService.get_records(
        page=page,
        limit=limit,
        source=source,
        search=search,
    )
