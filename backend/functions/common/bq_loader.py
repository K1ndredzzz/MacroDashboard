"""
BigQuery loader for ingesting data
"""
import logging
import hashlib
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from google.cloud import bigquery
from google.cloud.exceptions import GoogleCloudError

from .config import config

logger = logging.getLogger(__name__)


class BigQueryLoader:
    """Load data into BigQuery tables"""

    def __init__(self):
        self.client = bigquery.Client(project=config.GCP_PROJECT_ID)

    def insert_raw_payload(
        self,
        run_id: str,
        source: str,
        endpoint: str,
        request_url: str,
        request_params: Dict[str, Any],
        http_status: int,
        response_body: Any,
        is_success: bool,
        error_message: Optional[str] = None
    ) -> None:
        """
        Insert raw API payload into macro_raw.api_payload

        Args:
            run_id: ETL run identifier
            source: Data source (fred, world_bank)
            endpoint: API endpoint identifier
            request_url: Full request URL
            request_params: Request parameters
            http_status: HTTP status code
            response_body: Raw API response
            is_success: Whether request succeeded
            error_message: Error details if failed
        """
        table_id = f"{config.GCP_PROJECT_ID}.{config.BQ_DATASET_RAW}.api_payload"

        # Generate payload hash
        response_hash = hashlib.sha256(
            json.dumps(response_body, sort_keys=True).encode()
        ).hexdigest()

        row = {
            "payload_id": self._generate_uuid(),
            "run_id": run_id,
            "source": source,
            "endpoint": endpoint,
            "request_url": request_url,
            "request_params": json.dumps(request_params) if request_params else None,
            "http_status": http_status,
            "response_body": json.dumps(response_body) if response_body else None,
            "response_hash": response_hash,
            "ingested_at": datetime.utcnow().isoformat(),
            "is_success": is_success,
            "error_message": error_message
        }

        try:
            errors = self.client.insert_rows_json(table_id, [row])
            if errors:
                logger.error(f"Failed to insert raw payload: {errors}")
                raise Exception(f"BigQuery insert errors: {errors}")

            logger.info(f"Inserted raw payload for {source}/{endpoint}")

        except GoogleCloudError as e:
            logger.error(f"BigQuery error: {str(e)}")
            raise

    def insert_observations(
        self,
        observations: List[Dict[str, Any]],
        run_id: str
    ) -> Dict[str, int]:
        """
        Insert observations into macro_core.fact_observation using MERGE

        Args:
            observations: List of observation records
            run_id: ETL run identifier

        Returns:
            Dict with inserted_count and updated_count
        """
        if not observations:
            return {"inserted_count": 0, "updated_count": 0}

        target_table_id = f"{config.GCP_PROJECT_ID}.{config.BQ_DATASET_CORE}.fact_observation"

        try:
            # Build VALUES clause for MERGE
            values_rows = []
            for obs in observations:
                # Escape and format values
                series_uid = obs['series_uid'].replace("'", "\\'")
                source = obs['source'].replace("'", "\\'")
                indicator_code = obs['indicator_code'].replace("'", "\\'")
                country_code = obs['country_code'].replace("'", "\\'")
                observation_date = obs['observation_date']

                # Format timestamps for BigQuery (replace 'T' with space, remove 'Z')
                observation_ts_formatted = obs['observation_ts'].replace('T', ' ').replace('Z', '')
                value = obs.get('value')

                # Handle value_text with proper escaping
                if obs.get('value_text'):
                    escaped_value_text = obs['value_text'].replace("'", "\\'")
                    value_text = f"'{escaped_value_text}'"
                else:
                    value_text = 'NULL'

                revision_no = obs['revision_no']
                is_preliminary = 'TRUE' if obs['is_preliminary'] else 'FALSE'

                # Handle release_date
                if obs.get('release_date'):
                    release_date = f"'{obs['release_date']}'"
                else:
                    release_date = 'NULL'

                quality_status = obs['quality_status'].replace("'", "\\'")
                row_hash = obs['row_hash'].replace("'", "\\'")

                # Format ingested_at timestamp
                ingested_at_formatted = obs['ingested_at'].replace('T', ' ').replace('Z', '')

                value_str = str(value) if value is not None else 'NULL'

                row = f"""(
                    '{series_uid}', '{source}', '{indicator_code}', '{country_code}',
                    DATE '{observation_date}', TIMESTAMP '{observation_ts_formatted}',
                    {value_str}, {value_text},
                    {revision_no}, {is_preliminary}, {release_date}, '{quality_status}',
                    '{run_id}', '{row_hash}', TIMESTAMP '{ingested_at_formatted}'
                )"""
                values_rows.append(row)

            values_clause = ",\n".join(values_rows)

            # Execute MERGE query with inline VALUES
            merge_query = f"""
            MERGE `{target_table_id}` T
            USING (
                SELECT * FROM UNNEST([
                    STRUCT<
                        series_uid STRING, source STRING, indicator_code STRING, country_code STRING,
                        observation_date DATE, observation_ts TIMESTAMP, value NUMERIC, value_text STRING,
                        revision_no INT64, is_preliminary BOOL, release_date DATE, quality_status STRING,
                        run_id STRING, row_hash STRING, ingested_at TIMESTAMP
                    >
                    {values_clause}
                ])
            ) S
            ON T.series_uid = S.series_uid
               AND T.observation_date = S.observation_date
               AND T.revision_no = S.revision_no
            WHEN MATCHED AND T.row_hash != S.row_hash THEN
              UPDATE SET
                value = S.value,
                value_text = S.value_text,
                quality_status = S.quality_status,
                row_hash = S.row_hash,
                ingested_at = S.ingested_at
            WHEN NOT MATCHED THEN
              INSERT (
                series_uid, source, indicator_code, country_code,
                observation_date, observation_ts, value, value_text,
                revision_no, is_preliminary, release_date, quality_status,
                run_id, row_hash, ingested_at
              )
              VALUES (
                S.series_uid, S.source, S.indicator_code, S.country_code,
                S.observation_date, S.observation_ts, S.value, S.value_text,
                S.revision_no, S.is_preliminary, S.release_date, S.quality_status,
                S.run_id, S.row_hash, S.ingested_at
              )
            """

            query_job = self.client.query(merge_query)
            result = query_job.result()

            # Get stats
            stats = {
                "inserted_count": result.num_dml_affected_rows or 0,
                "updated_count": 0  # BigQuery doesn't provide separate update count
            }

            logger.info(f"MERGE completed: {stats}")
            return stats

        except GoogleCloudError as e:
            logger.error(f"BigQuery MERGE error: {str(e)}")
            raise

    def log_etl_run(
        self,
        run_id: str,
        pipeline: str,
        source: str,
        started_at: datetime,
        status: str,
        ended_at: Optional[datetime] = None,
        fetched_count: int = 0,
        inserted_count: int = 0,
        updated_count: int = 0,
        error_count: int = 0,
        retry_count: int = 0,
        error_detail: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log ETL run to macro_ops.etl_run_log

        Args:
            run_id: Unique run identifier
            pipeline: Pipeline name
            source: Data source
            started_at: Start timestamp
            status: Status (running/success/failed/partial)
            ended_at: End timestamp
            fetched_count: Number of records fetched
            inserted_count: Number of new records
            updated_count: Number of updated records
            error_count: Number of errors
            retry_count: Number of retries
            error_detail: Error details
        """
        table_id = f"{config.GCP_PROJECT_ID}.{config.BQ_DATASET_OPS}.etl_run_log"

        row = {
            "run_id": run_id,
            "pipeline": pipeline,
            "source": source,
            "started_at": started_at.isoformat(),
            "ended_at": ended_at.isoformat() if ended_at else None,
            "status": status,
            "fetched_count": fetched_count,
            "inserted_count": inserted_count,
            "updated_count": updated_count,
            "error_count": error_count,
            "retry_count": retry_count,
            "error_detail": json.dumps(error_detail) if error_detail else None
        }

        try:
            errors = self.client.insert_rows_json(table_id, [row])
            if errors:
                logger.error(f"Failed to log ETL run: {errors}")

        except GoogleCloudError as e:
            logger.error(f"Failed to log ETL run: {str(e)}")

    @staticmethod
    def _generate_uuid() -> str:
        """Generate UUID for records"""
        import uuid
        return str(uuid.uuid4())
