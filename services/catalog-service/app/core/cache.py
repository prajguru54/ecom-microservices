"""
Redis cache utilities.
"""
import json
from typing import Any, Optional

import redis.asyncio as redis
from pydantic import BaseModel

from app.core.config import settings

# Global Redis client
redis_client: Optional[redis.Redis] = None


async def get_redis_client() -> redis.Redis:
    """
    Get Redis client instance.
    """
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(settings.REDIS_URL)
    return redis_client


async def close_redis_client() -> None:
    """
    Close Redis client connection.
    """
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None


async def get_from_cache(key: str) -> Optional[Any]:
    """
    Get value from cache.
    """
    try:
        client = await get_redis_client()
        value = await client.get(key)
        if value:
            return json.loads(value)
        return None
    except Exception:
        # Fail silently on cache errors
        return None


async def set_in_cache(key: str, value: Any, ttl: int = None) -> bool:
    """
    Set value in cache with optional TTL.
    """
    try:
        client = await get_redis_client()
        ttl = ttl or settings.CACHE_TTL_SECONDS
        
        if isinstance(value, BaseModel):
            json_value = value.model_dump_json()
        else:
            json_value = json.dumps(value, default=str)
        
        await client.setex(key, ttl, json_value)
        return True
    except Exception:
        # Fail silently on cache errors
        return False


async def delete_from_cache(key: str) -> bool:
    """
    Delete value from cache.
    """
    try:
        client = await get_redis_client()
        await client.delete(key)
        return True
    except Exception:
        # Fail silently on cache errors
        return False


async def delete_pattern_from_cache(pattern: str) -> bool:
    """
    Delete keys matching pattern from cache.
    """
    try:
        client = await get_redis_client()
        keys = await client.keys(pattern)
        if keys:
            await client.delete(*keys)
        return True
    except Exception:
        # Fail silently on cache errors
        return False


def make_cache_key(*parts: str) -> str:
    """
    Create a cache key from parts.
    """
    return ":".join(str(part) for part in parts)