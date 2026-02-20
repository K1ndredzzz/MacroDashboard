"""
BigQuery repository for data access
"""
import logging
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from google.cloud import bigquery
from google.cloud.exceptions import GoogleCloudError

from ..core.config import settings

logger = logging.getLogger(__name__)


class BigQueryRepository:
    """Repository for BigQuery data access"""

    def __init__(self):
        self.client = bigquery.Client(project=settings.GCP_PROJECT_ID)
        self.dataset_core = settings.BQ_DATASET_CORE
        self.dataset_mart = settings.BQ_DATASET_MART

    def get_indicators(self) -> List[Dict[str, Any]]:
        """
        Get all active indicators

        Returns:
            List of indicator metadata
        """
        query = f"""
        SELECT
            series_uid,
            source,
            source_series_code,
            indicator_code,
            indicator_name,
            category,
            frequency,
            unit,
            currency,
            country_code,
            is_active,
            first_obs_date,
            last_obs_date
        FROM `{settings.GCP_PROJECT_ID}.{self.dataset_core}.dim_series`
        WHERE is_active = TRUE
        ORDER BY category, indicator_code
        """

        try:
            query_job = self.client.query(query)
            results = query_job.result()

            indicators = []
            for row in results:
                indicators.append(dict(row))

            logger.info(f"Retrieved {len(indicators)} indicators")
            return indicators

        except GoogleCloudError as e:
            logger.error(f"BigQuery error: {str(e)}")
            raise

    def get_series_data(
        self,
        indicator_code: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 1000
    ) -> Dict[str, Any]:
        """
        Get time series data for an indicator

        Args:
            indicator_code: Indicator code
            start_date: Start date filter
            end_date: End date filter
            limit: Maximum number of observations

        Returns:
            Dict with series metadata and observations
        """
        # Build query
        where_clauses = [
            f"f.indicator_code = '{indicator_code}'",
            "f.quality_status = 'ok'"
        ]

        if start_date:
            where_clauses.append(f"f.observation_date >= '{start_date}'")
        if end_date:
            where_clauses.append(f"f.observation_date <= '{end_date}'")

        where_clause = " AND ".join(where_clauses)

        query = f"""
        SELECT
            s.indicator_code,
            s.indicator_name,
            s.unit,
            f.observation_date,
            f.value,
            f.value_text,
            f.quality_status
        FROM `{settings.GCP_PROJECT_ID}.{self.dataset_core}.fact_observation` f
        JOIN `{settings.GCP_PROJECT_ID}.{self.dataset_core}.dim_series` s
            ON f.series_uid = s.series_uid
        WHERE {where_clause}
        ORDER BY f.observation_date DESC
        LIMIT {limit}
        """

        try:
            query_job = self.client.query(query)
            results = query_job.result()

            observations = []
            metadata = None

            for row in results:
                if metadata is None:
                    metadata = {
                        "indicator_code": row["indicator_code"],
                        "indicator_name": row["indicator_name"],
                        "unit": row["unit"]
                    }

                observations.append({
                    "observation_date": row["observation_date"],
                    "value": row["value"],
                    "value_text": row["value_text"],
                    "quality_status": row["quality_status"]
                })

            if metadata is None:
                raise ValueError(f"Indicator not found: {indicator_code}")

            logger.info(f"Retrieved {len(observations)} observations for {indicator_code}")

            return {
                **metadata,
                "observations": observations,
                "count": len(observations)
            }

        except GoogleCloudError as e:
            logger.error(f"BigQuery error: {str(e)}")
            raise

    def get_latest_snapshot(self) -> List[Dict[str, Any]]:
        """
        Get latest values for all indicators

        Returns:
            List of latest value snapshots
        """
        query = f"""
        SELECT
            indicator_code,
            indicator_name,
            category,
            as_of_date,
            latest_value,
            prev_value,
            delta_abs,
            delta_pct,
            unit,
            updated_at
        FROM `{settings.GCP_PROJECT_ID}.{self.dataset_mart}.v_latest_snapshot`
        ORDER BY category, indicator_code
        """

        try:
            query_job = self.client.query(query)
            results = query_job.result()

            snapshots = []
            for row in results:
                snapshots.append(dict(row))

            logger.info(f"Retrieved {len(snapshots)} latest snapshots")
            return snapshots

        except GoogleCloudError as e:
            logger.error(f"BigQuery error: {str(e)}")
            raise
