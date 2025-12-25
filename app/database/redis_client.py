from redis.asyncio import Redis

from app.config.settings import get_settings

settings = get_settings()

import re


def normalize_prefix(value: str) -> str:
    return re.sub(r"[^a-z0-9_]+", "_", value.lower()).strip("_")


redis_client: Redis = Redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
)


class NamespacedCache:
    def __init__(self, redis: Redis, prefix: str):
        self._redis = redis
        self._prefix = prefix

    def _key(self, *parts: str) -> str:
        return f"{self._prefix}:" + ":".join(parts)

    async def setex(self, ttl: int, value: str, *parts: str):
        return await self._redis.setex(self._key(*parts), ttl, value)

    async def get(self, *parts: str):
        return await self._redis.get(self._key(*parts))

    async def delete(self, *parts: str):
        return await self._redis.delete(self._key(*parts))


cache = NamespacedCache(redis_client, normalize_prefix(settings.APP_NAME))
