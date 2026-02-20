"""
FRED data extractor
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from common.http_client import HTTPClient
from common.config import config

logger = logging.getLogger(__name__)


class FREDExtractor:
    """Extract data from FRED API"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or config.FRED_API_KEY
        self.base_url = config.FRED_API_BASE
        self.http_client = HTTPClient()

    def fetch_series(
        self,
        series_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fetch time series data from FRED

        Args:
            series_id: FRED series ID (e.g., DGS10)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            Dict with observations and metadata
        """
        url = f"{self.base_url}/series/observations"

        params = {
            "series_id": series_id,
            "api_key": self.api_key,
            "file_type": "json"
        }

        if start_date:
            params["observation_start"] = start_date
        if end_date:
            params["observation_end"] = end_date

        try:
            response = self.http_client.get(url, params=params)
            data = response.json()

            logger.info(f"Fetched {len(data.get('observations', []))} observations for {series_id}")

            return {
                "series_id": series_id,
                "observations": data.get("observations", []),
                "count": data.get("count", 0),
                "request_url": response.url,
                "request_params": params,
                "http_status": response.status_code
            }

        except Exception as e:
            logger.error(f"Failed to fetch {series_id}: {str(e)}")
            raise

    def fetch_series_info(self, series_id: str) -> Dict[str, Any]:
        """
        Fetch series metadata from FRED

        Args:
            series_id: FRED series ID

        Returns:
            Dict with series metadata
        """
        url = f"{self.base_url}/series"

        params = {
            "series_id": series_id,
            "api_key": self.api_key,
            "file_type": "json"
        }

        try:
            response = self.http_client.get(url, params=params)
            data = response.json()

            series_info = data.get("seriess", [{}])[0]
            logger.info(f"Fetched metadata for {series_id}")

            return series_info

        except Exception as e:
            logger.error(f"Failed to fetch metadata for {series_id}: {str(e)}")
            raise

    def fetch_multiple_series(
        self,
        series_ids: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch multiple series data

        Args:
            series_ids: List of FRED series IDs
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            List of series data dicts
        """
        results = []

        for series_id in series_ids:
            try:
                data = self.fetch_series(series_id, start_date, end_date)
                results.append(data)

            except Exception as e:
                logger.error(f"Failed to fetch {series_id}, continuing with others")
                results.append({
                    "series_id": series_id,
                    "error": str(e),
                    "observations": []
                })

        return results

    def close(self):
        """Close HTTP client"""
        self.http_client.close()
