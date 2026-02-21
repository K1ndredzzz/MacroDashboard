"""
Pydantic schemas for API requests and responses
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
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


class YieldCurvePoint(BaseModel):
    """Single point on yield curve"""
    maturity: str
    rate: Optional[Decimal] = None


class YieldCurveResponse(BaseModel):
    """Yield curve response"""
    observation_date: date
    points: List[YieldCurvePoint]
    spread_10y_2y: Optional[Decimal] = None
    curve_shape: str  # 'normal', 'inverted', 'flat'


class CorrelationRow(BaseModel):
    """Single row in correlation matrix"""
    indicator: str
    correlations: Dict[str, Optional[float]]


class StrongCorrelation(BaseModel):
    """Strong correlation pair"""
    indicator1: str
    indicator2: str
    correlation: float


class CorrelationMatrixResponse(BaseModel):
    """Correlation matrix response"""
    matrix: List[CorrelationRow]
    strong_correlations: List[StrongCorrelation]
    start_date: str
    end_date: str
    window_days: int
    observation_count: int


class EventResponse(BaseModel):
    """Event response"""
    event_id: int
    event_name: str
    event_date: date
    event_type: str
    description: Optional[str] = None
    severity: Optional[str] = None
    created_at: datetime


class EventImpactResponse(BaseModel):
    """Event impact analysis response"""
    event: EventResponse
    indicators: List[Dict[str, Any]]
    analysis_window_days: int


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime
    version: str
    services: dict
