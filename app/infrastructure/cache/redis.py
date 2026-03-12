import redis.asyncio as redis
from app.infrastructure.config import settings
from app.core.logger import logger

redis_client = redis.Redis(
    host=settings.redis_host, port=settings.redis_port, decode_responses=True
)


async def redis_lifespan_check():
    try:
        await redis_client.ping()
        logger.info("Redis connection established")
    except Exception as e:
        logger.critical(f"Redis connection failed: {e}")
        raise RuntimeError("Redis connection failed")

    await redis_client.close()
