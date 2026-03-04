"""
PostgreSQL repository for data access
"""
import logging
from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta
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

    @staticmethod
    def _is_fixed_income_indicator(indicator_code: str) -> bool:
        """Identify yield/rate style indicators that should use bps deltas."""
        code = (indicator_code or "").upper()
        if not code:
            return False

        return (
            (code.startswith("US") and code.endswith("Y")) or
            ("FEDFUNDS" in code) or
            code.endswith("RATE") or
            ("YIELD" in code)
        )

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

    def get_yield_curve(
        self,
        observation_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Get yield curve data for US Treasury rates

        Args:
            observation_date: Specific date (defaults to latest)

        Returns:
            Dict with yield curve points and spread
        """
        # If no date specified, get latest date
        if not observation_date:
            date_query = """
            SELECT MAX(observation_date) as latest_date
            FROM core.fact_observations
            WHERE indicator_code IN ('US2Y', 'US10Y')
            AND quality_status = 'ok'
            """

            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(date_query)
                    result = cur.fetchone()
                    observation_date = result['latest_date'] if result else None
        else:
            # If date specified, find the closest available date (on or before)
            date_query = """
            SELECT MAX(observation_date) as closest_date
            FROM core.fact_observations
            WHERE indicator_code IN ('US2Y', 'US10Y')
            AND quality_status = 'ok'
            AND observation_date <= %s
            """

            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(date_query, (observation_date,))
                    result = cur.fetchone()
                    if result and result['closest_date']:
                        observation_date = result['closest_date']
                    else:
                        # If no data on or before, get earliest available
                        cur.execute("""
                            SELECT MIN(observation_date) as earliest_date
                            FROM core.fact_observations
                            WHERE indicator_code IN ('US2Y', 'US10Y')
                            AND quality_status = 'ok'
                        """)
                        result = cur.fetchone()
                        observation_date = result['earliest_date'] if result else None

        if not observation_date:
            raise ValueError("No yield curve data available")

        # Get rates for specified date
        query = """
        SELECT
            f.indicator_code,
            f.observation_date,
            f.value
        FROM core.fact_observations f
        WHERE f.observation_date = %s
        AND f.indicator_code IN ('US2Y', 'US10Y')
        AND f.quality_status = 'ok'
        ORDER BY f.indicator_code
        """

        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(query, (observation_date,))
                    rows = cur.fetchall()

            if not rows:
                raise ValueError(f"No yield curve data for date: {observation_date}")

            # Build points
            points = []
            rates = {}
            for row in rows:
                code = row['indicator_code']
                value = row['value']
                rates[code] = value

                if code == 'US2Y':
                    points.append({'maturity': '2Y', 'rate': value})
                elif code == 'US10Y':
                    points.append({'maturity': '10Y', 'rate': value})

            def maturity_to_months(maturity: str) -> int:
                """Convert maturity labels (e.g. 3M, 2Y) to months for stable ascending sorting."""
                if not maturity:
                    return 10**9

                label = str(maturity).strip().upper()
                if len(label) < 2:
                    return 10**9

                unit = label[-1]
                try:
                    value = float(label[:-1])
                except ValueError:
                    return 10**9

                if unit == 'D':
                    return int(value / 30)
                if unit == 'W':
                    return int((value * 7) / 30)
                if unit == 'M':
                    return int(value)
                if unit == 'Y':
                    return int(value * 12)
                return 10**9

            # Always render yield-curve points from short tenor to long tenor.
            points.sort(key=lambda point: maturity_to_months(point['maturity']))

            # Calculate spread and determine curve shape
            spread = None
            curve_shape = 'unknown'

            if 'US10Y' in rates and 'US2Y' in rates:
                spread = rates['US10Y'] - rates['US2Y']

                if spread > 0.5:
                    curve_shape = 'normal'
                elif spread < -0.1:
                    curve_shape = 'inverted'
                else:
                    curve_shape = 'flat'

            logger.info(f"Retrieved yield curve for {observation_date}: spread={spread}, shape={curve_shape}")

            return {
                'observation_date': observation_date,
                'points': points,
                'spread_10y_2y': spread,
                'curve_shape': curve_shape
            }

        except Exception as e:
            logger.error(f"PostgreSQL error: {str(e)}")
            raise

    def get_events(
        self,
        event_type: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Get historical events

        Args:
            event_type: Filter by event type
            start_date: Filter by start date
            end_date: Filter by end date

        Returns:
            List of events
        """
        where_clauses = []
        params = []

        if event_type:
            where_clauses.append("event_type = %s")
            params.append(event_type)
        if start_date:
            where_clauses.append("event_date >= %s")
            params.append(start_date)
        if end_date:
            where_clauses.append("event_date <= %s")
            params.append(end_date)

        where_clause = " AND ".join(where_clauses) if where_clauses else "TRUE"

        query = f"""
        SELECT
            event_id,
            event_name,
            event_date,
            event_type,
            description,
            severity,
            created_at
        FROM core.dim_events
        WHERE {where_clause}
        ORDER BY event_date DESC
        """

        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(query, params)
                    events = [dict(row) for row in cur.fetchall()]

            logger.info(f"Retrieved {len(events)} events")
            return events

        except Exception as e:
            logger.error(f"PostgreSQL error: {str(e)}")
            raise

    def get_event_impact(
        self,
        event_id: int,
        indicator_codes: List[str],
        window_days: int = 30
    ) -> Dict[str, Any]:
        """
        Get event impact on indicators

        Args:
            event_id: Event ID
            indicator_codes: List of indicator codes to analyze
            window_days: Days before and after event to analyze

        Returns:
            Dict with event and indicator changes
        """
        # Get event details
        event_query = """
        SELECT
            event_id,
            event_name,
            event_date,
            event_type,
            description,
            severity,
            created_at
        FROM core.dim_events
        WHERE event_id = %s
        """

        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(event_query, (event_id,))
                    event = cur.fetchone()

            if not event:
                raise ValueError(f"Event not found: {event_id}")

            event_date = event['event_date']
            start_date = event_date - timedelta(days=window_days)
            end_date = event_date + timedelta(days=window_days)

            # Get indicator data around event
            indicators_data = []
            for code in indicator_codes:
                try:
                    series_data = self.get_series_data(
                        indicator_code=code,
                        start_date=start_date,
                        end_date=end_date,
                        limit=1000
                    )

                    # Calculate before/after values
                    observations = sorted(
                        series_data['observations'],
                        key=lambda obs: obs['observation_date']
                    )
                    before_obs = [o for o in observations if o['observation_date'] < event_date]
                    after_obs = [o for o in observations if o['observation_date'] >= event_date]

                    before_value = before_obs[-1]['value'] if before_obs else None
                    after_value = after_obs[0]['value'] if after_obs else None

                    change_abs = None
                    change_pct = None
                    change_bps = None
                    if before_value is not None and after_value is not None:
                        # Absolute change in percentage points.
                        change_abs = after_value - before_value

                        # Relative percentage change (kept for non-rate indicators).
                        if before_value != 0:
                            change_pct = (change_abs / before_value) * 100

                        # Fixed-income change should be expressed in basis points.
                        if self._is_fixed_income_indicator(code):
                            change_bps = change_abs * 100

                    indicators_data.append({
                        'indicator_code': code,
                        'indicator_name': series_data['indicator_name'],
                        'before_value': float(before_value) if before_value is not None else None,
                        'after_value': float(after_value) if after_value is not None else None,
                        'change_abs': float(change_abs) if change_abs is not None else None,
                        'change_pct': float(change_pct) if change_pct is not None else None,
                        'change_bps': float(change_bps) if change_bps is not None else None,
                        'observations': observations
                    })

                except Exception as e:
                    logger.warning(f"Failed to get impact for {code}: {str(e)}")
                    continue

            logger.info(f"Retrieved event impact for event {event_id}, {len(indicators_data)} indicators")

            return {
                'event': dict(event),
                'indicators': indicators_data,
                'analysis_window_days': window_days
            }

        except Exception as e:
            logger.error(f"PostgreSQL error: {str(e)}")
            raise
