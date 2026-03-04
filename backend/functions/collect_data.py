#!/usr/bin/env python3
"""
Standalone script for FRED data collection to PostgreSQL
Run this script via cron for periodic data updates
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

import logging
import psycopg2
from datetime import datetime, timedelta
from typing import List, Dict, Any
import uuid

from fred.extractor import FREDExtractor
from fred.transformer import FREDTransformer
from common.series_config import COLLECTOR_BASE_SERIES, build_fred_series

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_db_connection():
    """Get PostgreSQL connection from environment variables"""
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        database=os.getenv("POSTGRES_DB", "macro_dashboard"),
        user=os.getenv("POSTGRES_USER", "macro_user"),
        password=os.getenv("POSTGRES_PASSWORD", "")
    )


def insert_observations(conn, observations: List[Dict[str, Any]]):
    """Insert observations into PostgreSQL"""
    if not observations:
        return 0

    insert_query = """
    INSERT INTO core.fact_observations
        (indicator_code, observation_date, value, value_text, quality_status)
    VALUES (%s, %s, %s, %s, %s)
    ON CONFLICT (indicator_code, observation_date)
    DO UPDATE SET
        value = EXCLUDED.value,
        value_text = EXCLUDED.value_text,
        quality_status = EXCLUDED.quality_status
    """

    inserted = 0
    with conn.cursor() as cur:
        for obs in observations:
            try:
                cur.execute(insert_query, (
                    obs['indicator_code'],
                    obs['observation_date'],
                    obs['value'],
                    obs.get('value_text'),
                    obs['quality_status']
                ))
                inserted += 1
            except Exception as e:
                logger.error(f"Error inserting observation for {obs.get('indicator_code')}: {e}")
                continue

    conn.commit()
    return inserted


def log_etl_run(conn, run_id: str, source: str, status: str,
                records_processed: int, records_inserted: int,
                error_message: str = None):
    """Log ETL run to ops.etl_runs table"""
    insert_query = """
    INSERT INTO ops.etl_runs
        (run_id, source, status, started_at, completed_at,
         records_processed, records_inserted, error_message)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    with conn.cursor() as cur:
        cur.execute(insert_query, (
            run_id,
            source,
            status,
            datetime.utcnow(),
            datetime.utcnow(),
            records_processed,
            records_inserted,
            error_message
        ))
    conn.commit()


def main():
    """Main data collection function"""
    run_id = str(uuid.uuid4())
    logger.info(f"Starting FRED data collection - Run ID: {run_id}")

    # Get FRED API key
    fred_api_key = os.getenv("FRED_API_KEY")
    if not fred_api_key:
        logger.error("FRED_API_KEY not set in environment")
        return 1

    # Connect to database
    try:
        conn = get_db_connection()
        logger.info("Connected to PostgreSQL")
    except Exception as e:
        logger.error(f"Failed to connect to PostgreSQL: {e}")
        return 1

    # Initialize extractor and transformer
    extractor = FREDExtractor(api_key=fred_api_key)
    transformer = FREDTransformer()

    # Limit pull window to avoid oversized cron runs and API throttling.
    lookback_days_raw = os.getenv("LOOKBACK_DAYS", "30")
    try:
        lookback_days = max(1, int(lookback_days_raw))
    except ValueError:
        logger.warning(f"Invalid LOOKBACK_DAYS={lookback_days_raw}, fallback to 30")
        lookback_days = 30

    total_processed = 0
    total_inserted = 0
    errors = []
    series_to_fetch = build_fred_series(COLLECTOR_BASE_SERIES, logger=logger)
    logger.info(f"Collector series count: {len(series_to_fetch)}")

    # Fetch data for each series
    for series_id in series_to_fetch:
        try:
            logger.info(f"Fetching {series_id}...")

            # Extract raw data
            raw_data = extractor.fetch_series(
                series_id=series_id,
                start_date=(datetime.utcnow() - timedelta(days=lookback_days)).strftime("%Y-%m-%d")
            )

            if not raw_data or 'observations' not in raw_data:
                logger.warning(f"No data returned for {series_id}")
                continue

            # Transform to standard format
            series_data = {
                "series_id": series_id,
                "observations": raw_data['observations']
            }
            observations = transformer.transform_observations(
                series_data=series_data,
                run_id=run_id
            )

            total_processed += len(observations)

            # Insert into database
            inserted = insert_observations(conn, observations)
            total_inserted += inserted

            logger.info(f"✓ {series_id}: {inserted}/{len(observations)} observations inserted")

        except Exception as e:
            error_msg = f"Error processing {series_id}: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)
            continue

    # Log ETL run
    status = "success" if not errors else "partial_success" if total_inserted > 0 else "failed"
    error_message = "; ".join(errors) if errors else None

    try:
        log_etl_run(
            conn=conn,
            run_id=run_id,
            source="fred",
            status=status,
            records_processed=total_processed,
            records_inserted=total_inserted,
            error_message=error_message
        )
    except Exception as e:
        # ETL log write failures should not mark the whole cron run as failed.
        logger.warning(f"Failed to write ETL run log: {e}")

    conn.close()

    logger.info(f"Data collection complete - Run ID: {run_id}")
    logger.info(f"Lookback days: {lookback_days}")
    logger.info(f"Processed: {total_processed}, Inserted: {total_inserted}")

    # Return 0 for success or partial_success (most data collected successfully)
    return 0 if status in ["success", "partial_success"] else 1


if __name__ == "__main__":
    sys.exit(main())
