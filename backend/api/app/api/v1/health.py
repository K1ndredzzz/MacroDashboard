"""
Health check endpoint
"""
from fastapi import APIRouter
from datetime import datetime

from ...schemas.indicators import HealthResponse
from ...repositories.bigquery_repo import BigQueryRepository
from ...services.cache import CacheService
from ...core.config import settings

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint

    Returns:
        Service health status
    """
    services = {}

    # Check Redis
    try:
        cache = CacheService()
        services["redis"] = "healthy" if cache.ping() else "unhealthy"
    except:
        services["redis"] = "unhealthy"

    # Check BigQuery
    try:
        bq_repo = BigQueryRepository()
        # Simple query to test connection
        query = f"SELECT 1 as test FROM `{settings.GCP_PROJECT_ID}.{settings.BQ_DATASET_CORE}.dim_series` LIMIT 1"
        bq_repo.client.query(query).result()
        services["bigquery"] = "healthy"
    except:
        services["bigquery"] = "unhealthy"

    # Overall status
    all_healthy = all(status == "healthy" for status in services.values())
    status = "healthy" if all_healthy else "degraded"

    return {
        "status": status,
        "timestamp": datetime.utcnow(),
        "version": settings.APP_VERSION,
        "services": services
    }
