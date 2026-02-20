"""
FRED data ingestion Cloud Function
"""
import sys
import os
from pathlib import Path

# Add parent directory to path for module imports
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

import logging
import functions_framework
from datetime import datetime, timedelta
from typing import Dict, Any
import uuid

from fred.extractor import FREDExtractor
from fred.transformer import FREDTransformer
from common.bq_loader import BigQueryLoader
from common.config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# FRED series to fetch
FRED_SERIES = [
    "DGS2",    # US 2Y Treasury
    "DGS10",   # US 10Y Treasury
    "DGS30",   # US 30Y Treasury
    "DEXUSEU", # EUR/USD
    "DEXJPUS", # USD/JPY
    "DEXUSUK", # GBP/USD
    "DCOILWTICO",  # WTI Oil
    # "GOLDAMGBD228NLBM",  # Gold - Removed: LBMA data restricted by API
    "CPIAUCSL",  # CPI
    "CPILFESL",  # Core CPI
    "PPIACO",    # PPI
    "UNRATE",    # Unemployment Rate
    "PAYEMS"     # Nonfarm Payrolls
]


@functions_framework.http
def ingest_fred_http(request):
    """
    HTTP Cloud Function to ingest FRED data

    Args:
        request: HTTP request object

    Returns:
        HTTP response with ingestion results
    """
    # Generate run ID
    run_id = str(uuid.uuid4())
    started_at = datetime.utcnow()

    logger.info(f"Starting FRED ingestion, run_id: {run_id}")

    # Validate configuration
    try:
        config.validate()
    except ValueError as e:
        logger.error(f"Configuration error: {str(e)}")
        return {"error": str(e)}, 500

    # Initialize components
    extractor = FREDExtractor()
    transformer = FREDTransformer()
    loader = BigQueryLoader()

    # Parse request parameters
    request_json = request.get_json(silent=True) or {}
    lookback_days = request_json.get("lookback_days", 7)

    # Calculate date range
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=lookback_days)

    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")

    logger.info(f"Fetching data from {start_date_str} to {end_date_str}")

    # Log ETL run start
    loader.log_etl_run(
        run_id=run_id,
        pipeline="ingest_fred",
        source="fred",
        started_at=started_at,
        status="running"
    )

    total_fetched = 0
    total_inserted = 0
    total_updated = 0
    error_count = 0
    errors = []

    try:
        # Fetch data for all series
        for series_id in FRED_SERIES:
            try:
                logger.info(f"Processing {series_id}")

                # Extract
                series_data = extractor.fetch_series(
                    series_id,
                    start_date=start_date_str,
                    end_date=end_date_str
                )

                # Log raw payload
                loader.insert_raw_payload(
                    run_id=run_id,
                    source="fred",
                    endpoint=f"series/observations/{series_id}",
                    request_url=series_data["request_url"],
                    request_params=series_data["request_params"],
                    http_status=series_data["http_status"],
                    response_body=series_data["observations"],
                    is_success=True
                )

                # Transform
                observations = transformer.transform_observations(series_data, run_id)
                total_fetched += len(observations)

                # Load
                if observations:
                    stats = loader.insert_observations(observations, run_id)
                    total_inserted += stats["inserted_count"]
                    total_updated += stats["updated_count"]

                logger.info(f"Completed {series_id}: {len(observations)} observations")

            except Exception as e:
                error_count += 1
                error_msg = f"Failed to process {series_id}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)

                # Log failed payload
                try:
                    loader.insert_raw_payload(
                        run_id=run_id,
                        source="fred",
                        endpoint=f"series/observations/{series_id}",
                        request_url="",
                        request_params={},
                        http_status=0,
                        response_body={},
                        is_success=False,
                        error_message=str(e)
                    )
                except:
                    pass

        # Determine final status
        if error_count == 0:
            status = "success"
        elif error_count < len(FRED_SERIES):
            status = "partial"
        else:
            status = "failed"

        # Log ETL run completion
        ended_at = datetime.utcnow()
        loader.log_etl_run(
            run_id=run_id,
            pipeline="ingest_fred",
            source="fred",
            started_at=started_at,
            ended_at=ended_at,
            status=status,
            fetched_count=total_fetched,
            inserted_count=total_inserted,
            updated_count=total_updated,
            error_count=error_count,
            error_detail={"errors": errors} if errors else None
        )

        # Build response
        duration = (ended_at - started_at).total_seconds()

        response = {
            "run_id": run_id,
            "status": status,
            "duration_seconds": duration,
            "series_processed": len(FRED_SERIES) - error_count,
            "series_failed": error_count,
            "observations_fetched": total_fetched,
            "observations_inserted": total_inserted,
            "observations_updated": total_updated,
            "errors": errors if errors else None
        }

        logger.info(f"FRED ingestion completed: {response}")

        return response, 200 if status == "success" else 207

    except Exception as e:
        logger.error(f"Fatal error in FRED ingestion: {str(e)}")

        # Log failure
        loader.log_etl_run(
            run_id=run_id,
            pipeline="ingest_fred",
            source="fred",
            started_at=started_at,
            ended_at=datetime.utcnow(),
            status="failed",
            error_count=1,
            error_detail={"error": str(e)}
        )

        return {"error": str(e), "run_id": run_id}, 500

    finally:
        extractor.close()
