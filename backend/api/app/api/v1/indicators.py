"""
API v1 endpoints for indicators
"""
import logging
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import date, datetime

from ...schemas.indicators import (
    IndicatorResponse,
    SeriesResponse,
    DashboardOverviewResponse,
    LatestValueResponse
)
from ...repositories.postgres_repo import PostgresRepository
from ...services.cache import CacheService
from ...core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services
db_repo = PostgresRepository()
cache = CacheService()


@router.get("/indicators", response_model=List[IndicatorResponse])
async def get_indicators():
    """
    Get all active indicators

    Returns list of indicator metadata
    """
    cache_key = cache.generate_key("indicators", "list")

    # Try cache first
    cached = cache.get(cache_key)
    if cached:
        return cached

    try:
        indicators = db_repo.get_indicators()
        cache.set(cache_key, indicators, settings.CACHE_TTL_INDICATORS)
        return indicators

    except Exception as e:
        logger.error(f"Failed to get indicators: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve indicators")


@router.get("/indicators/{indicator_code}/series", response_model=SeriesResponse)
async def get_series(
    indicator_code: str,
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    limit: int = Query(1000, ge=1, le=10000, description="Maximum observations")
):
    """
    Get time series data for an indicator

    Args:
        indicator_code: Indicator code (e.g., US10Y, EURUSD)
        start_date: Optional start date filter
        end_date: Optional end date filter
        limit: Maximum number of observations

    Returns:
        Time series data with observations
    """
    cache_key = cache.generate_key(
        "series",
        indicator_code,
        str(start_date) if start_date else "all",
        str(end_date) if end_date else "all",
        str(limit)
    )

    # Try cache first
    cached = cache.get(cache_key)
    if cached:
        return cached

    try:
        series_data = db_repo.get_series_data(
            indicator_code=indicator_code,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )

        # Determine TTL based on indicator category
        ttl = settings.CACHE_TTL_RATES  # Default
        cache.set(cache_key, series_data, ttl)

        return series_data

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get series {indicator_code}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve series data")


@router.get("/dashboard/overview", response_model=DashboardOverviewResponse)
async def get_dashboard_overview():
    """
    Get dashboard overview with latest values for all indicators

    Returns:
        Latest values for all indicators
    """
    cache_key = cache.generate_key("dashboard", "overview")

    # Try cache first
    cached = cache.get(cache_key)
    if cached:
        return cached

    try:
        snapshots = db_repo.get_latest_snapshot()

        response = {
            "indicators": snapshots,
            "as_of": datetime.utcnow()
        }

        cache.set(cache_key, response, settings.CACHE_TTL_RATES)
        return response

    except Exception as e:
        logger.error(f"Failed to get dashboard overview: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve dashboard data")
