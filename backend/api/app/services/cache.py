"""
Redis cache service
"""
import json
import logging
from typing import Optional, Any
import redis

from ..core.config import settings

logger = logging.getLogger(__name__)


class CacheService:
    """Redis cache service"""

    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            decode_responses=True
        )

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        try:
            value = self.redis_client.get(key)
            if value:
                logger.debug(f"Cache hit: {key}")
                return json.loads(value)
            logger.debug(f"Cache miss: {key}")
            return None

        except Exception as e:
            logger.error(f"Cache get error: {str(e)}")
            return None

    def set(self, key: str, value: Any, ttl: int) -> bool:
        """
        Set value in cache

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds

        Returns:
            True if successful
        """
        try:
            self.redis_client.setex(
                key,
                ttl,
                json.dumps(value, default=str)
            )
            logger.debug(f"Cache set: {key} (TTL: {ttl}s)")
            return True

        except Exception as e:
            logger.error(f"Cache set error: {str(e)}")
            return False

    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            self.redis_client.delete(key)
            logger.debug(f"Cache delete: {key}")
            return True

        except Exception as e:
            logger.error(f"Cache delete error: {str(e)}")
            return False

    def ping(self) -> bool:
        """Check if Redis is available"""
        try:
            return self.redis_client.ping()
        except:
            return False

    def generate_key(self, *parts: str) -> str:
        """Generate cache key from parts"""
        return "macro:" + ":".join(str(p) for p in parts)
