"""
Dashboard stats and summary endpoints.
"""

from fastapi import APIRouter, HTTPException
from backend.services.scraper_service import ScraperService

router = APIRouter(tags=["Dashboard"])


@router.get("/dashboard")
def get_dashboard_data():
    """
    Get consolidated statistics for dashboard cards, source details, and execution audit.
    """
    return ScraperService.get_dashboard_stats()


@router.get("/summary")
def get_summary_report():
    """
    Get raw summary_report.json data.
    """
    data = ScraperService.get_summary_data()
    if data is None:
        raise HTTPException(
            status_code=404,
            detail="Summary report not found. Run the scraper first.",
        )
    return data
