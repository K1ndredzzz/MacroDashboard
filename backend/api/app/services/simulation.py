"""
Shock simulation service for scenario analysis
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import date, timedelta
from enum import Enum
import numpy as np

from .correlation import CorrelationService
from ..repositories.postgres_repo import PostgresRepository

logger = logging.getLogger(__name__)


class ShockType(str, Enum):
    """Types of economic shocks"""
    INTEREST_RATE = "interest_rate"
    EXCHANGE_RATE = "exchange_rate"
    OIL_PRICE = "oil_price"


class SimulationService:
    """Service for simulating economic shocks and their impacts"""

    def __init__(self):
        self.correlation_service = CorrelationService()
        self.db_repo = PostgresRepository()

        # Sensitivity coefficients by indicator category
        self.sensitivity_map = {
            # Interest rate sensitivity
            'interest_rate': {
                'rates': 1.0,      # Direct impact
                'fx': 0.7,         # Strong impact on currencies
                'equity': 0.6,     # Moderate impact on stocks
                'commodity': 0.4,  # Moderate impact on commodities
                'inflation': 0.3,  # Indirect impact
                'labor': 0.2       # Weak impact
            },
            # Exchange rate sensitivity
            'exchange_rate': {
                'fx': 1.0,         # Direct impact
                'commodity': 0.6,  # Strong impact (dollar-denominated)
                'inflation': 0.5,  # Moderate impact (import prices)
                'equity': 0.4,     # Moderate impact
                'rates': 0.3,      # Indirect impact
                'labor': 0.2       # Weak impact
            },
            # Oil price sensitivity
            'oil_price': {
                'commodity': 1.0,  # Direct impact
                'inflation': 0.7,  # Strong impact (energy costs)
                'fx': 0.5,         # Moderate impact (petrodollar)
                'equity': 0.4,     # Moderate impact (sector-specific)
                'rates': 0.3,      # Indirect impact (inflation expectations)
                'labor': 0.2       # Weak impact
            }
        }

    def simulate_shock(
        self,
        shock_type: ShockType,
        shock_magnitude: float,
        target_indicator: str,
        affected_indicators: Optional[List[str]] = None,
        window_days: int = 90,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Simulate economic shock and calculate impacts

        Args:
            shock_type: Type of shock (interest_rate, exchange_rate, oil_price)
            shock_magnitude: Magnitude of shock (in percentage or basis points)
            target_indicator: The indicator being shocked (e.g., 'US10Y', 'EURUSD', 'WTI')
            affected_indicators: List of indicators to analyze (optional)
            window_days: Historical window for correlation calculation
            start_date: Optional start date for correlation window
            end_date: Optional end date for correlation window

        Returns:
            Dict with shock details and impact predictions
        """
        # Default affected indicators if not specified
        if not affected_indicators:
            affected_indicators = self._get_default_indicators(shock_type)
        else:
            affected_indicators = list(dict.fromkeys(affected_indicators))

        # Use the same default date behavior as correlation matrix endpoint.
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=365)

        all_indicators = []
        for code in [target_indicator] + affected_indicators:
            if code not in all_indicators:
                all_indicators.append(code)

        try:
            corr_data = self.correlation_service.calculate_correlation_matrix(
                indicator_codes=all_indicators,
                start_date=start_date,
                end_date=end_date,
                window_days=window_days
            )
        except Exception as e:
            logger.error(f"Failed to calculate correlations: {str(e)}")
            raise ValueError(f"Cannot simulate shock: {str(e)}")

        # Extract correlation matrix
        corr_matrix = {}
        for row in corr_data['matrix']:
            indicator = row['indicator']
            corr_matrix[indicator] = row['correlations']

        # Calculate impacts
        impacts = []
        for indicator in affected_indicators:
            corr_value = corr_matrix.get(target_indicator, {}).get(indicator, 0)
            if corr_value is None:
                corr_value = 0

            if indicator == target_indicator:
                # Direct impact on target
                impact = self._calculate_direct_impact(
                    shock_magnitude=shock_magnitude,
                    shock_type=shock_type
                )
            else:
                # Indirect impact via correlation
                impact = self._calculate_indirect_impact(
                    shock_magnitude=shock_magnitude,
                    shock_type=shock_type,
                    correlation=corr_value,
                    target_category=self._get_indicator_category(target_indicator),
                    affected_category=self._get_indicator_category(indicator)
                )

            impacts.append({
                'indicator_code': indicator,
                'indicator_name': self._get_indicator_name(indicator),
                'correlation': corr_value,
                'predicted_change': impact['predicted_change'],
                'confidence_lower': impact['confidence_lower'],
                'confidence_upper': impact['confidence_upper'],
                'impact_level': impact['impact_level']
            })

        # Sort by absolute impact
        impacts.sort(key=lambda x: abs(x['predicted_change']), reverse=True)

        logger.info(f"Simulated {shock_type} shock: {shock_magnitude}% on {target_indicator}, "
                   f"analyzed {len(impacts)} indicators")

        return {
            'shock_type': shock_type,
            'target_indicator': target_indicator,
            'shock_magnitude': shock_magnitude,
            'impacts': impacts,
            'correlation_window_days': window_days,
            'observation_count': corr_data['observation_count']
        }

    def _calculate_direct_impact(
        self,
        shock_magnitude: float,
        shock_type: ShockType
    ) -> Dict[str, Any]:
        """Calculate direct impact on the shocked indicator"""
        # Direct impact is the shock magnitude itself
        predicted_change = shock_magnitude

        # Confidence interval (±20% of shock magnitude)
        confidence_range = abs(shock_magnitude) * 0.2
        confidence_lower = predicted_change - confidence_range
        confidence_upper = predicted_change + confidence_range

        return {
            'predicted_change': predicted_change,
            'confidence_lower': confidence_lower,
            'confidence_upper': confidence_upper,
            'impact_level': 'direct'
        }

    def _calculate_indirect_impact(
        self,
        shock_magnitude: float,
        shock_type: ShockType,
        correlation: float,
        target_category: str,
        affected_category: str
    ) -> Dict[str, Any]:
        """Calculate indirect impact via correlation and sensitivity"""
        # Get sensitivity coefficient
        sensitivity = self.sensitivity_map.get(shock_type, {}).get(affected_category, 0.3)

        # Calculate base impact
        base_impact = correlation * shock_magnitude * sensitivity

        # Adjust for correlation strength
        if abs(correlation) > 0.7:
            impact_level = 'strong'
            confidence_multiplier = 0.3
        elif abs(correlation) > 0.4:
            impact_level = 'moderate'
            confidence_multiplier = 0.5
        else:
            impact_level = 'weak'
            confidence_multiplier = 0.7

        # Calculate confidence interval
        confidence_range = abs(base_impact) * confidence_multiplier
        confidence_lower = base_impact - confidence_range
        confidence_upper = base_impact + confidence_range

        return {
            'predicted_change': base_impact,
            'confidence_lower': confidence_lower,
            'confidence_upper': confidence_upper,
            'impact_level': impact_level
        }

    def _get_indicator_category(self, indicator_code: str) -> str:
        """Get category for an indicator"""
        # Simple mapping based on indicator code patterns
        if any(x in indicator_code for x in ['Y', 'FEDFUNDS', 'RATE']):
            return 'rates'
        elif any(x in indicator_code for x in ['USD', 'EUR', 'JPY', 'CNY']):
            return 'fx'
        elif any(x in indicator_code for x in ['WTI', 'GOLD', 'CRUDE']):
            return 'commodity'
        elif any(x in indicator_code for x in ['CPI', 'PPI', 'INFLATION']):
            return 'inflation'
        elif any(x in indicator_code for x in ['UNRATE', 'PAYEMS', 'CIVPART', 'AHETPI']):
            return 'labor'
        else:
            return 'equity'

    def _get_indicator_name(self, indicator_code: str) -> str:
        """Get display name for an indicator"""
        try:
            series_data = self.db_repo.get_series_data(
                indicator_code=indicator_code,
                limit=1
            )
            return series_data.get('indicator_name', indicator_code)
        except Exception:
            return indicator_code

    def _get_default_indicators(self, shock_type: ShockType) -> List[str]:
        """Get default indicators to analyze for each shock type"""
        if shock_type == ShockType.INTEREST_RATE:
            return ['US10Y', 'US2Y', 'EURUSD', 'USDJPY', 'WTI', 'FEDFUNDS']
        elif shock_type == ShockType.EXCHANGE_RATE:
            return ['EURUSD', 'USDJPY', 'USDCNY', 'WTI', 'US10Y', 'US2Y']
        elif shock_type == ShockType.OIL_PRICE:
            return ['WTI', 'CPI_US', 'EURUSD', 'US10Y', 'USDJPY']
        else:
            return ['US10Y', 'US2Y', 'EURUSD', 'WTI']
