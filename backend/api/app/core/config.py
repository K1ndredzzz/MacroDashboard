"""
Configuration settings for FastAPI application
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "Macro Dashboard API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # API
    API_V1_PREFIX: str = "/api/v1"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # GCP
    GCP_PROJECT_ID: str = "gen-lang-client-0815236933"
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None

    # BigQuery
    BQ_DATASET_CORE: str = "macro_core"
    BQ_DATASET_MART: str = "macro_mart"

    # Redis (optional)
    REDIS_ENABLED: bool = False
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None

    # Cache TTL (seconds)
    CACHE_TTL_RATES: int = 300  # 5 minutes
    CACHE_TTL_FX: int = 300
    CACHE_TTL_COMMODITIES: int = 600  # 10 minutes
    CACHE_TTL_INFLATION: int = 21600  # 6 hours
    CACHE_TTL_INDICATORS: int = 86400  # 24 hours

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",  # Vite dev server
        "http://localhost:8080"
    ]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
