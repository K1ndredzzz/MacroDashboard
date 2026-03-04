"""
Simulation API endpoints
"""
import logging
from fastapi import APIRouter, HTTPException, status

from ...services.simulation import SimulationService
from ...schemas.simulation import ShockSimulationRequest, ShockSimulationResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/shock", response_model=ShockSimulationResponse, status_code=status.HTTP_200_OK)
async def simulate_shock(request: ShockSimulationRequest):
    """
    Simulate economic shock and predict impacts

    Simulates the impact of an economic shock (interest rate, exchange rate, or oil price)
    on various economic indicators using historical correlations and sensitivity coefficients.

    **Algorithm**:
    - Impact = Correlation × Shock Magnitude × Sensitivity × Confidence Adjustment
    - Sensitivity coefficients vary by indicator category
    - Confidence intervals based on correlation strength

    **Shock Types**:
    - `interest_rate`: Interest rate changes (in basis points)
    - `exchange_rate`: Currency depreciation/appreciation (in percentage)
    - `oil_price`: Oil price changes (in percentage)

    **Example**:
    ```json
    {
      "shock_type": "interest_rate",
      "shock_magnitude": 1.0,
      "target_indicator": "US10Y",
      "affected_indicators": ["US2Y", "EURUSD", "WTI"],
      "window_days": 90
    }
    ```
    """
    try:
        simulation_service = SimulationService()

        result = simulation_service.simulate_shock(
            shock_type=request.shock_type,
            shock_magnitude=request.shock_magnitude,
            target_indicator=request.target_indicator,
            affected_indicators=request.affected_indicators,
            window_days=request.window_days,
            start_date=request.start_date,
            end_date=request.end_date
        )

        return ShockSimulationResponse(**result)

    except ValueError as e:
        logger.warning(f"Invalid simulation request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Simulation error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to simulate shock"
        )
