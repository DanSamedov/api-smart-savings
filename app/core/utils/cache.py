# app/core/utils/cache.py

import fnmatch
import json
from typing import Any, Callable, Optional

from pydantic import BaseModel
from redis.asyncio import Redis

from app.core.config import settings
from app.core.middleware.logging import logger
from app.core.utils.helpers import mask_data


async def cache_or_get(
    redis: Redis, key: str, fetch_func: Callable[[], Any], ttl: int = settings.CACHE_TTL
):
    """
    Check if key exists in redis, if yes, return json of cached data
    If no, add key and data to redis.

    Args:
        redis (Redis): Redis client
        key (str): key id stored in redis
        fetch_func (Callable): function to retrieve data
        ttl (int): Time to live for cached data - in seconds

    Returns:
        Data requested
    """
    cached = await redis.get(key)
    if cached:
        logger.info(f"CACHE HIT: {mask_data(key)}")
        # Redis returns bytes, so decode first
        cached_str = cached.decode("utf-8") if isinstance(cached, bytes) else cached
        try:
            data = json.loads(cached_str)
        except json.JSONDecodeError:
            # If for some reason cached value is raw string, fallback
            data = cached_str
        return data

    # Cache miss
    logger.info(f"CACHE MISS: {mask_data(key)}")
    data = await fetch_func()

    if isinstance(data, BaseModel):
        data = data.model_dump()

    # Save to Redis as JSON string
    await redis.set(key, json.dumps(data, default=str), ex=ttl)
    return data


async def invalidate_cache(redis: Redis, pattern: str):
    """
    Delete all keys matching a pattern from Redis.

    Args:
        redis (Redis): Redis client
        pattern (str): Pattern to match keys, e.g. 'user_current:*'
    """
    # Scan keys instead of KEYS for performance on large datasets
    cursor = b"0"
    while cursor:
        cursor, keys = await redis.scan(cursor=cursor, match=pattern, count=100)
        if keys:
            await redis.delete(*keys)
            logger.info(f"CACHE INVALIDATED: {mask_data(pattern)}")
        if cursor == 0 or cursor == b"0":
            break
