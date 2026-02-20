"""
HTTP client with retry logic and error handling
"""
import time
import logging
from typing import Dict, Any, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config import config

logger = logging.getLogger(__name__)


class HTTPClient:
    """HTTP client with automatic retry and backoff"""

    def __init__(self):
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create requests session with retry strategy"""
        session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=config.MAX_RETRIES,
            backoff_factor=config.RETRY_BACKOFF_FACTOR,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = config.REQUEST_TIMEOUT
    ) -> requests.Response:
        """
        Execute GET request with retry logic

        Args:
            url: Request URL
            params: Query parameters
            headers: Request headers
            timeout: Request timeout in seconds

        Returns:
            Response object

        Raises:
            requests.RequestException: On request failure
        """
        try:
            logger.info(f"GET request to {url}")
            response = self.session.get(
                url,
                params=params,
                headers=headers,
                timeout=timeout
            )
            response.raise_for_status()
            return response

        except requests.exceptions.Timeout as e:
            logger.error(f"Request timeout: {url}")
            raise

        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error {e.response.status_code}: {url}")
            raise

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {url}, error: {str(e)}")
            raise

    def close(self):
        """Close session"""
        self.session.close()


def is_retryable_error(status_code: int) -> bool:
    """Check if HTTP status code is retryable"""
    return status_code in [429, 500, 502, 503, 504]


def is_client_error(status_code: int) -> bool:
    """Check if HTTP status code is client error (non-retryable)"""
    return 400 <= status_code < 500 and status_code != 429
