"""
Correlation analysis service
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import date, timedelta
import numpy as np
import pandas as pd

from ..repositories.postgres_repo import PostgresRepository

logger = logging.getLogger(__name__)


class CorrelationService:
    """Service for calculating correlation between indicators"""

    def __init__(self):
        self.db_repo = PostgresRepository()

    def calculate_correlation_matrix(
        self,
        indicator_codes: List[str],
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        window_days: int = 90
    ) -> Dict[str, Any]:
        """
        Calculate correlation matrix for given indicators

        Args:
            indicator_codes: List of indicator codes
            start_date: Start date for analysis
            end_date: End date for analysis
            window_days: Rolling window size in days

        Returns:
            Dict with correlation matrix and metadata
        """
        # Default to last 1 year if not specified
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=365)

        # Fetch data for all indicators
        data_frames = []
        for code in indicator_codes:
            try:
                series_data = self.db_repo.get_series_data(
                    indicator_code=code,
                    start_date=start_date,
                    end_date=end_date,
                    limit=10000
                )

                # Convert to DataFrame
                df = pd.DataFrame(series_data['observations'])
                df['observation_date'] = pd.to_datetime(df['observation_date'])
                df['value'] = pd.to_numeric(df['value'], errors='coerce')
                df = df[['observation_date', 'value']].rename(columns={'value': code})
                df = df.set_index('observation_date').sort_index()

                data_frames.append(df)

            except Exception as e:
                logger.warning(f"Failed to fetch data for {code}: {str(e)}")
                continue

        if len(data_frames) < 2:
            raise ValueError("Need at least 2 indicators with valid data")

        # Merge all data frames
        merged_df = data_frames[0]
        for df in data_frames[1:]:
            merged_df = merged_df.join(df, how='outer')

        # Forward fill missing values (up to 5 days)
        merged_df = merged_df.ffill(limit=5)

        # Drop rows with any remaining NaN
        merged_df = merged_df.dropna()

        if len(merged_df) < window_days:
            raise ValueError(f"Insufficient data points: {len(merged_df)} < {window_days}")

        # Calculate correlation matrix
        corr_matrix = merged_df.corr(method='pearson')

        # Convert to list of dicts for JSON serialization
        matrix_data = []
        for i, row_name in enumerate(corr_matrix.index):
            row_data = {
                'indicator': row_name,
                'correlations': {}
            }
            for j, col_name in enumerate(corr_matrix.columns):
                value = corr_matrix.iloc[i, j]
                row_data['correlations'][col_name] = float(value) if not np.isnan(value) else None

            matrix_data.append(row_data)

        # Find strong correlations (|r| > 0.7, excluding diagonal)
        strong_correlations = []
        for i, row_name in enumerate(corr_matrix.index):
            for j, col_name in enumerate(corr_matrix.columns):
                if i < j:  # Only upper triangle
                    value = corr_matrix.iloc[i, j]
                    if abs(value) > 0.7:
                        strong_correlations.append({
                            'indicator1': row_name,
                            'indicator2': col_name,
                            'correlation': float(value)
                        })

        logger.info(f"Calculated correlation matrix for {len(indicator_codes)} indicators, "
                   f"{len(merged_df)} observations, found {len(strong_correlations)} strong correlations")

        return {
            'matrix': matrix_data,
            'strong_correlations': strong_correlations,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'window_days': window_days,
            'observation_count': len(merged_df)
        }
