"""
Health check endpoint
"""
from fastapi import APIRouter
from datetime import datetime

from ...schemas.indicators import HealthResponse
from ...repositories.postgres_repo import PostgresRepository
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

    # Check PostgreSQL
    try:
        db_repo = PostgresRepository()
        # Simple query to test connection
        with db_repo._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
        services["postgres"] = "healthy"
    except:
        services["postgres"] = "unhealthy"

    # Overall status
    all_healthy = all(status == "healthy" for status in services.values())
    status = "healthy" if all_healthy else "degraded"

    return {
        "status": status,
        "timestamp": datetime.utcnow(),
        "version": settings.APP_VERSION,
        "services": services
    }
