"""
Pydantic schemas for simulation API
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class ShockType(str, Enum):
    """Types of economic shocks"""
    INTEREST_RATE = "interest_rate"
    EXCHANGE_RATE = "exchange_rate"
    OIL_PRICE = "oil_price"


class ShockSimulationRequest(BaseModel):
    """Request schema for shock simulation"""
    shock_type: ShockType = Field(..., description="Type of economic shock")
    shock_magnitude: float = Field(..., description="Magnitude of shock in percentage or basis points", ge=-100, le=100)
    target_indicator: str = Field(..., description="Indicator code being shocked (e.g., 'US10Y', 'EURUSD', 'WTI')")
    affected_indicators: Optional[List[str]] = Field(None, description="List of indicators to analyze (optional)")
    window_days: int = Field(90, description="Historical window for correlation calculation", ge=30, le=365)

    class Config:
        json_schema_extra = {
            "example": {
                "shock_type": "interest_rate",
                "shock_magnitude": 1.0,
                "target_indicator": "US10Y",
                "affected_indicators": ["US2Y", "EURUSD", "WTI", "USDJPY"],
                "window_days": 90
            }
        }


class ImpactPrediction(BaseModel):
    """Predicted impact on a single indicator"""
    indicator_code: str
    indicator_name: str
    correlation: float = Field(..., description="Correlation with target indicator")
    predicted_change: float = Field(..., description="Predicted percentage change")
    confidence_lower: float = Field(..., description="Lower bound of confidence interval")
    confidence_upper: float = Field(..., description="Upper bound of confidence interval")
    impact_level: str = Field(..., description="Impact level: direct, strong, moderate, weak")


class ShockSimulationResponse(BaseModel):
    """Response schema for shock simulation"""
    shock_type: ShockType
    target_indicator: str
    shock_magnitude: float
    impacts: List[ImpactPrediction]
    correlation_window_days: int
    observation_count: int

    class Config:
        json_schema_extra = {
            "example": {
                "shock_type": "interest_rate",
                "target_indicator": "US10Y",
                "shock_magnitude": 1.0,
                "impacts": [
                    {
                        "indicator_code": "US10Y",
                        "indicator_name": "US 10-Year Treasury Yield",
                        "correlation": 1.0,
                        "predicted_change": 1.0,
                        "confidence_lower": 0.8,
                        "confidence_upper": 1.2,
                        "impact_level": "direct"
                    },
                    {
                        "indicator_code": "US2Y",
                        "indicator_name": "US 2-Year Treasury Yield",
                        "correlation": 0.85,
                        "predicted_change": 0.72,
                        "confidence_lower": 0.50,
                        "confidence_upper": 0.94,
                        "impact_level": "strong"
                    }
                ],
                "correlation_window_days": 90,
                "observation_count": 63
            }
        }
