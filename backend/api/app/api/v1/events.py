"""
Events API endpoints for historical event backtest
"""
import logging
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Query, status

from ...repositories.postgres_repo import PostgresRepository

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("", status_code=status.HTTP_200_OK)
async def get_events():
    """
    Get all historical events

    Returns a list of all events in the database, ordered by date descending.
    """
    try:
        repo = PostgresRepository()

        query = """
            SELECT
                event_id,
                event_name,
                event_date,
                event_type,
                description,
                severity
            FROM core.dim_events
            ORDER BY event_date DESC
        """

        events = repo.execute_query(query)

        return [
            {
                "event_id": row[0],
                "event_name": row[1],
                "event_date": row[2].isoformat() if row[2] else None,
                "event_type": row[3],
                "description": row[4],
                "severity": row[5]
            }
            for row in events
        ]

    except Exception as e:
        logger.error(f"Failed to fetch events: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch events"
        )


@router.get("/{event_id}/impact", status_code=status.HTTP_200_OK)
async def get_event_impact(
    event_id: int,
    indicator_codes: str = Query(..., description="Comma-separated indicator codes"),
    window_days: int = Query(30, ge=1, le=90, description="Analysis window in days")
):
    """
    Get event impact analysis

    Analyzes the impact of a specific event on given indicators by comparing
    values before and after the event within the specified window.

    Args:
        event_id: Event ID
        indicator_codes: Comma-separated list of indicator codes (e.g., "US10Y,US2Y,EURUSD")
        window_days: Number of days before and after the event to analyze (default: 30)

    Returns:
        Event details and indicator impacts with before/after values and percentage changes
    """
    try:
        repo = PostgresRepository()

        # Get event details
        event_query = """
            SELECT
                event_id,
                event_name,
                event_date,
                event_type,
                description,
                severity
            FROM core.dim_events
            WHERE event_id = %s
        """

        event_result = repo.execute_query(event_query, (event_id,))

        if not event_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event {event_id} not found"
            )

        event_row = event_result[0]
        event_date = event_row[2]

        event = {
            "event_id": event_row[0],
            "event_name": event_row[1],
            "event_date": event_date.isoformat() if event_date else None,
            "event_type": event_row[3],
            "description": event_row[4],
            "severity": event_row[5]
        }

        # Parse indicator codes
        codes = [code.strip() for code in indicator_codes.split(",")]

        # Calculate date ranges
        start_date = event_date - timedelta(days=window_days)
        end_date = event_date + timedelta(days=window_days)

        indicators = []

        for code in codes:
            # Get indicator name
            indicator_query = """
                SELECT indicator_name
                FROM core.dim_indicators
                WHERE indicator_code = %s
            """

            indicator_result = repo.execute_query(indicator_query, (code,))

            if not indicator_result:
                logger.warning(f"Indicator {code} not found")
                continue

            indicator_name = indicator_result[0][0]

            # Get observations around the event
            obs_query = """
                SELECT
                    observation_date,
                    value
                FROM core.fact_observations
                WHERE indicator_code = %s
                    AND observation_date BETWEEN %s AND %s
                ORDER BY observation_date
            """

            observations = repo.execute_query(obs_query, (code, start_date, end_date))

            if not observations:
                logger.warning(f"No observations found for {code} around event date")
                indicators.append({
                    "indicator_code": code,
                    "indicator_name": indicator_name,
                    "before_value": None,
                    "after_value": None,
                    "change_pct": None,
                    "observations": []
                })
                continue

            # Split observations into before and after
            before_obs = [obs for obs in observations if obs[0] < event_date]
            after_obs = [obs for obs in observations if obs[0] >= event_date]

            # Calculate before and after values (average of closest observations)
            before_value = None
            after_value = None
            change_pct = None

            if before_obs:
                # Use the last observation before the event
                before_value = float(before_obs[-1][1])

            if after_obs:
                # Use the first observation after the event
                after_value = float(after_obs[0][1])

            if before_value is not None and after_value is not None and before_value != 0:
                change_pct = ((after_value - before_value) / before_value) * 100

            indicators.append({
                "indicator_code": code,
                "indicator_name": indicator_name,
                "before_value": before_value,
                "after_value": after_value,
                "change_pct": change_pct,
                "observations": [
                    {
                        "observation_date": obs[0].isoformat() if obs[0] else None,
                        "value": str(obs[1])
                    }
                    for obs in observations
                ]
            })

        return {
            "event": event,
            "indicators": indicators,
            "analysis_window_days": window_days
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to analyze event impact: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze event impact"
        )
