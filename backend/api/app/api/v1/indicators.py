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
    LatestValueResponse,
    YieldCurveResponse,
    CorrelationMatrixResponse,
    EventResponse,
    EventImpactResponse
)
from ...repositories.postgres_repo import PostgresRepository
from ...services.cache import CacheService
from ...services.correlation import CorrelationService
from ...core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services
db_repo = PostgresRepository()
cache = CacheService()
correlation_service = CorrelationService()


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


@router.get("/indicators/yield-curve", response_model=YieldCurveResponse)
async def get_yield_curve(
    observation_date: Optional[date] = Query(None, description="Observation date (YYYY-MM-DD), defaults to latest")
):
    """
    Get US Treasury yield curve data

    Args:
        observation_date: Optional specific date (defaults to latest available)

    Returns:
        Yield curve with 2Y and 10Y rates, spread, and curve shape
    """
    cache_key = cache.generate_key(
        "yield_curve",
        str(observation_date) if observation_date else "latest"
    )

    # Try cache first
    cached = cache.get(cache_key)
    if cached:
        return cached

    try:
        curve_data = db_repo.get_yield_curve(observation_date=observation_date)
        cache.set(cache_key, curve_data, settings.CACHE_TTL_RATES)
        return curve_data

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get yield curve: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve yield curve data")


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


@router.get("/analytics/correlation", response_model=CorrelationMatrixResponse)
async def get_correlation_matrix(
    indicator_codes: str = Query(..., description="Comma-separated indicator codes"),
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    window_days: int = Query(90, ge=30, le=365, description="Rolling window size in days")
):
    """
    Calculate correlation matrix for given indicators

    Args:
        indicator_codes: Comma-separated list of indicator codes (e.g., "US10Y,US2Y,EURUSD")
        start_date: Optional start date
        end_date: Optional end date
        window_days: Rolling window size (30-365 days)

    Returns:
        Correlation matrix with strong correlations highlighted
    """
    # Parse indicator codes
    codes = [code.strip() for code in indicator_codes.split(',')]

    if len(codes) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 indicator codes")

    if len(codes) > 20:
        raise HTTPException(status_code=400, detail="Maximum 20 indicators allowed")

    cache_key = cache.generate_key(
        "correlation",
        indicator_codes,
        str(start_date) if start_date else "auto",
        str(end_date) if end_date else "auto",
        str(window_days)
    )

    # Try cache first
    cached = cache.get(cache_key)
    if cached:
        return cached

    try:
        result = correlation_service.calculate_correlation_matrix(
            indicator_codes=codes,
            start_date=start_date,
            end_date=end_date,
            window_days=window_days
        )

        cache.set(cache_key, result, settings.CACHE_TTL_RATES)
        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to calculate correlation: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to calculate correlation matrix")


@router.get("/events", response_model=List[EventResponse])
async def get_events(
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)")
):
    """
    Get historical events

    Args:
        event_type: Optional event type filter
        start_date: Optional start date filter
        end_date: Optional end date filter

    Returns:
        List of historical events
    """
    cache_key = cache.generate_key(
        "events",
        event_type or "all",
        str(start_date) if start_date else "all",
        str(end_date) if end_date else "all"
    )

    # Try cache first
    cached = cache.get(cache_key)
    if cached:
        return cached

    try:
        events = db_repo.get_events(
            event_type=event_type,
            start_date=start_date,
            end_date=end_date
        )

        cache.set(cache_key, events, settings.CACHE_TTL_INDICATORS)
        return events

    except Exception as e:
        logger.error(f"Failed to get events: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve events")


@router.get("/events/{event_id}/impact", response_model=EventImpactResponse)
async def get_event_impact(
    event_id: int,
    indicator_codes: str = Query(..., description="Comma-separated indicator codes"),
    window_days: int = Query(30, ge=7, le=90, description="Analysis window in days")
):
    """
    Get event impact analysis

    Args:
        event_id: Event ID
        indicator_codes: Comma-separated list of indicator codes
        window_days: Days before and after event to analyze (7-90)

    Returns:
        Event impact analysis with indicator changes
    """
    # Parse indicator codes
    codes = [code.strip() for code in indicator_codes.split(',')]

    if len(codes) < 1:
        raise HTTPException(status_code=400, detail="Need at least 1 indicator code")

    if len(codes) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 indicators allowed")

    cache_key = cache.generate_key(
        "event_impact",
        str(event_id),
        indicator_codes,
        str(window_days)
    )

    # Try cache first
    cached = cache.get(cache_key)
    if cached:
        return cached

    try:
        result = db_repo.get_event_impact(
            event_id=event_id,
            indicator_codes=codes,
            window_days=window_days
        )

        cache.set(cache_key, result, settings.CACHE_TTL_RATES)
        return result

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get event impact: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve event impact")




