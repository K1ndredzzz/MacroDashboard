"""
Configuration module for Cloud Functions
"""
import os
from typing import Optional
from pathlib import Path

# Load .env file if exists
try:
    from dotenv import load_dotenv
    # Look for .env in functions directory
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"Loaded .env from {env_path}")
except ImportError:
    pass  # dotenv not installed, use system env vars only

class Config:
    """Configuration settings"""

    # GCP Settings
    GCP_PROJECT_ID: str = os.getenv('GCP_PROJECT_ID', 'gen-lang-client-0815236933')
    GCP_REGION: str = os.getenv('GCP_REGION', 'us-central1')

    # BigQuery Settings
    BQ_DATASET_RAW: str = os.getenv('BQ_DATASET_RAW', 'macro_raw')
    BQ_DATASET_CORE: str = os.getenv('BQ_DATASET_CORE', 'macro_core')
    BQ_DATASET_OPS: str = os.getenv('BQ_DATASET_OPS', 'macro_ops')

    # Cloud Storage
    GCS_BUCKET_RAW: str = os.getenv('GCS_BUCKET_RAW', 'macro-dashboard-raw')

    # FRED API
    FRED_API_KEY: str = os.getenv('FRED_API_KEY', '').strip()
    FRED_API_BASE: str = 'https://api.stlouisfed.org/fred'

    # World Bank API
    WORLD_BANK_API_BASE: str = 'https://api.worldbank.org/v2'

    # Retry Settings
    MAX_RETRIES: int = 3
    RETRY_BACKOFF_FACTOR: float = 2.0
    RETRY_INITIAL_DELAY: float = 1.0

    # HTTP Settings
    REQUEST_TIMEOUT: int = 30

    @classmethod
    def validate(cls) -> None:
        """Validate required configuration"""
        if not cls.FRED_API_KEY:
            raise ValueError("FRED_API_KEY environment variable is required")
        if not cls.GCP_PROJECT_ID:
            raise ValueError("GCP_PROJECT_ID environment variable is required")

config = Config()
