"""
FRED data transformer - standardize data for BigQuery
"""
import logging
import hashlib
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from decimal import Decimal

logger = logging.getLogger(__name__)


class FREDTransformer:
    """Transform FRED data to standardized format"""

    # Mapping from FRED series ID to our indicator metadata
    SERIES_MAPPING = {
        "DGS2": {
            "series_uid": "fred:DGS2:US:D",
            "indicator_code": "US2Y",
            "country_code": "US"
        },
        "DGS10": {
            "series_uid": "fred:DGS10:US:D",
            "indicator_code": "US10Y",
            "country_code": "US"
        },
        "DGS30": {
            "series_uid": "fred:DGS30:US:D",
            "indicator_code": "US30Y",
            "country_code": "US"
        },
        "FEDFUNDS": {
            "series_uid": "fred:FEDFUNDS:US:M",
            "indicator_code": "FEDFUNDS",
            "country_code": "US"
        },
        "DEXUSEU": {
            "series_uid": "fred:DEXUSEU:US:D",
            "indicator_code": "EURUSD",
            "country_code": "US"
        },
        "DEXCHUS": {
            "series_uid": "fred:DEXCHUS:US:D",
            "indicator_code": "USDCNY",
            "country_code": "US"
        },
        "DEXJPUS": {
            "series_uid": "fred:DEXJPUS:US:D",
            "indicator_code": "USDJPY",
            "country_code": "US"
        },
        "DEXUSUK": {
            "series_uid": "fred:DEXUSUK:US:D",
            "indicator_code": "GBPUSD",
            "country_code": "US"
        },
        "DCOILWTICO": {
            "series_uid": "fred:DCOILWTICO:US:D",
            "indicator_code": "WTI",
            "country_code": "US"
        },
        "GOLDAMGBD228NLBM": {
            "series_uid": "fred:GOLDAMGBD228NLBM:US:D",
            "indicator_code": "GOLD",
            "country_code": "US"
        },
        "CPIAUCSL": {
            "series_uid": "fred:CPIAUCSL:US:M",
            "indicator_code": "CPI_US",
            "country_code": "US"
        },
        "CPILFESL": {
            "series_uid": "fred:CPILFESL:US:M",
            "indicator_code": "CPI_CORE_US",
            "country_code": "US"
        },
        "PPIACO": {
            "series_uid": "fred:PPIACO:US:M",
            "indicator_code": "PPI_US",
            "country_code": "US"
        },
        "UNRATE": {
            "series_uid": "fred:UNRATE:US:M",
            "indicator_code": "UNRATE_US",
            "country_code": "US"
        },
        "PAYEMS": {
            "series_uid": "fred:PAYEMS:US:M",
            "indicator_code": "PAYEMS_US",
            "country_code": "US"
        },
        "CIVPART": {
            "series_uid": "fred:CIVPART:US:M",
            "indicator_code": "CIVPART_US",
            "country_code": "US"
        },
        "AHETPI": {
            "series_uid": "fred:AHETPI:US:M",
            "indicator_code": "AHETPI_US",
            "country_code": "US"
        }
    }

    def transform_observations(
        self,
        series_data: Dict[str, Any],
        run_id: str
    ) -> List[Dict[str, Any]]:
        """
        Transform FRED observations to standardized format

        Args:
            series_data: Raw series data from FRED
            run_id: ETL run identifier

        Returns:
            List of standardized observation records
        """
        series_id = series_data["series_id"]
        observations = series_data.get("observations", [])

        if series_id not in self.SERIES_MAPPING:
            logger.warning(f"Unknown series ID: {series_id}")
            return []

        metadata = self.SERIES_MAPPING[series_id]
        transformed = []

        for obs in observations:
            try:
                record = self._transform_single_observation(
                    obs, series_id, metadata, run_id
                )
                if record:
                    transformed.append(record)

            except Exception as e:
                logger.error(f"Failed to transform observation: {obs}, error: {str(e)}")
                continue

        logger.info(f"Transformed {len(transformed)} observations for {series_id}")
        return transformed

    def _transform_single_observation(
        self,
        obs: Dict[str, Any],
        series_id: str,
        metadata: Dict[str, Any],
        run_id: str
    ) -> Optional[Dict[str, Any]]:
        """Transform single observation"""
        date_str = obs.get("date")
        value_str = obs.get("value")

        if not date_str or not value_str:
            return None

        # Handle missing values (FRED uses "." for missing)
        if value_str == ".":
            return None

        # Parse value
        try:
            value = float(value_str)
        except ValueError:
            logger.warning(f"Invalid value for {series_id} on {date_str}: {value_str}")
            return None

        # Validate value range
        quality_status = self._validate_value(series_id, value)

        # Generate row hash for change detection
        row_data = {
            "series_uid": metadata["series_uid"],
            "observation_date": date_str,
            "value": value
        }
        row_hash = hashlib.sha256(
            json.dumps(row_data, sort_keys=True).encode()
        ).hexdigest()

        return {
            "series_uid": metadata["series_uid"],
            "source": "fred",
            "indicator_code": metadata["indicator_code"],
            "country_code": metadata["country_code"],
            "observation_date": date_str,
            "observation_ts": f"{date_str}T00:00:00",  # Convert date to timestamp
            "value": value,
            "value_text": None,
            "revision_no": 0,
            "is_preliminary": False,
            "release_date": date_str,
            "quality_status": quality_status,
            "run_id": run_id,
            "row_hash": row_hash,
            "ingested_at": datetime.utcnow().isoformat()
        }

    def _validate_value(self, series_id: str, value: float) -> str:
        """
        Validate value range and return quality status

        Args:
            series_id: FRED series ID
            value: Numeric value

        Returns:
            Quality status: 'ok', 'warn', or 'error'
        """
        # Define reasonable ranges for different series types
        ranges = {
            # Interest rates: -5% to 20%
            "DGS2": (-5, 20),
            "DGS10": (-5, 20),
            "DGS30": (-5, 20),
            "FEDFUNDS": (-5, 20),
            # FX rates: must be positive
            "DEXUSEU": (0, float('inf')),
            "DEXCHUS": (0, float('inf')),
            "DEXJPUS": (0, float('inf')),
            "DEXUSUK": (0, float('inf')),
            # Commodities: must be positive
            "DCOILWTICO": (0, 500),
            "GOLDAMGBD228NLBM": (0, 5000),
            # Indices: must be positive
            "CPIAUCSL": (0, 1000),
            "CPILFESL": (0, 1000),
            "PPIACO": (0, 1000),
            # Unemployment: 0% to 30%
            "UNRATE": (0, 30),
            # Payrolls: must be positive (in thousands)
            "PAYEMS": (0, 200000),
            # Labor force participation: 0% to 100%
            "CIVPART": (0, 100),
            # Average hourly earnings: must be positive
            "AHETPI": (0, 200)
        }

        if series_id in ranges:
            min_val, max_val = ranges[series_id]
            if value < min_val or value > max_val:
                logger.warning(f"Value {value} out of range for {series_id}")
                return "warn"

        return "ok"
