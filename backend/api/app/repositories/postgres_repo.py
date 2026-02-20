"""
PostgreSQL repository for data access
"""
import logging
from typing import List, Optional, Dict, Any
from datetime import date, datetime
import psycopg2
from psycopg2.extras import RealDictCursor
import os

from ..core.config import settings

logger = logging.getLogger(__name__)


class PostgresRepository:
    """Repository for PostgreSQL data access"""

    def __init__(self):
        self.conn_params = {
            "host": os.getenv("POSTGRES_HOST", "localhost"),
            "port": int(os.getenv("POSTGRES_PORT", "5432")),
            "database": os.getenv("POSTGRES_DB", "macro_dashboard"),
            "user": os.getenv("POSTGRES_USER", "macro_user"),
            "password": os.getenv("POSTGRES_PASSWORD", ""),
        }

    def _get_connection(self):
        """Get database connection"""
        return psycopg2.connect(**self.conn_params)

    def get_indicators(self) -> List[Dict[str, Any]]:
        """
        Get all active indicators

        Returns:
            List of indicator metadata
        """
        query = """
        SELECT
            indicator_code,
            indicator_name,
            category,
            frequency,
            unit,
            source,
            country_code,
            is_active,
            first_obs_date,
            last_obs_date
        FROM core.dim_series
        WHERE is_active = TRUE
        ORDER BY category, indicator_code
        """

        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(query)
                    indicators = [dict(row) for row in cur.fetchall()]

            logger.info(f"Retrieved {len(indicators)} indicators")
            return indicators

        except Exception as e:
            logger.error(f"PostgreSQL error: {str(e)}")
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
            "f.indicator_code = %s",
            "f.quality_status = 'ok'"
        ]
        params = [indicator_code]

        if start_date:
            where_clauses.append("f.observation_date >= %s")
            params.append(start_date)
        if end_date:
            where_clauses.append("f.observation_date <= %s")
            params.append(end_date)

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
        FROM core.fact_observations f
        JOIN core.dim_series s ON f.indicator_code = s.indicator_code
        WHERE {where_clause}
        ORDER BY f.observation_date DESC
        LIMIT %s
        """
        params.append(limit)

        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(query, params)
                    rows = cur.fetchall()

            if not rows:
                raise ValueError(f"Indicator not found: {indicator_code}")

            metadata = {
                "indicator_code": rows[0]["indicator_code"],
                "indicator_name": rows[0]["indicator_name"],
                "unit": rows[0]["unit"]
            }

            observations = [
                {
                    "observation_date": row["observation_date"],
                    "value": row["value"],
                    "value_text": row["value_text"],
                    "quality_status": row["quality_status"]
                }
                for row in rows
            ]

            logger.info(f"Retrieved {len(observations)} observations for {indicator_code}")

            return {
                **metadata,
                "observations": observations,
                "count": len(observations)
            }

        except Exception as e:
            logger.error(f"PostgreSQL error: {str(e)}")
            raise

    def get_latest_snapshot(self) -> List[Dict[str, Any]]:
        """
        Get latest values for all indicators

        Returns:
            List of latest value snapshots
        """
        query = """
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
        FROM mart.v_latest_snapshot
        ORDER BY category, indicator_code
        """

        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(query)
                    snapshots = [dict(row) for row in cur.fetchall()]

            logger.info(f"Retrieved {len(snapshots)} latest snapshots")
            return snapshots

        except Exception as e:
            logger.error(f"PostgreSQL error: {str(e)}")
            raise
