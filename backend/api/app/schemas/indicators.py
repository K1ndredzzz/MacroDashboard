"""
Pydantic schemas for API requests and responses
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal


class IndicatorBase(BaseModel):
    """Base indicator schema"""
    indicator_code: str
    indicator_name: str
    category: str
    frequency: str
    unit: Optional[str] = None


class IndicatorResponse(IndicatorBase):
    """Indicator response schema"""
    source: str
    country_code: Optional[str] = None
    is_active: bool
    first_obs_date: Optional[date] = None
    last_obs_date: Optional[date] = None


class ObservationResponse(BaseModel):
    """Single observation response"""
    observation_date: date
    value: Optional[Decimal] = None
    value_text: Optional[str] = None
    quality_status: str = "ok"


class SeriesResponse(BaseModel):
    """Time series response"""
    indicator_code: str
    indicator_name: str
    unit: Optional[str] = None
    observations: List[ObservationResponse]
    count: int


class LatestValueResponse(BaseModel):
    """Latest value snapshot"""
    indicator_code: str
    indicator_name: str
    category: str
    as_of_date: date
    latest_value: Optional[Decimal] = None
    prev_value: Optional[Decimal] = None
    delta_abs: Optional[Decimal] = None
    delta_pct: Optional[Decimal] = None
    unit: Optional[str] = None
    updated_at: datetime


class DashboardOverviewResponse(BaseModel):
    """Dashboard overview response"""
    indicators: List[LatestValueResponse]
    as_of: datetime


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime
    version: str
    services: dict
