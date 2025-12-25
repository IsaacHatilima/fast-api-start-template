from redis.asyncio import Redis

from app.config.settings import get_settings

settings = get_settings()

redis_client: Redis = Redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
)
