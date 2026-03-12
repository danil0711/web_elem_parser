from datetime import timedelta
from app.core.logger import logger
from app.infrastructure.config import settings
from app.infrastructure.cache.redis import redis_client

REFRESH_TOKEN_PREFIX = "auth:refresh"


def _refresh_key(jti: str) -> str:
    return f"{REFRESH_TOKEN_PREFIX}:{jti}"


async def store_refresh_token(jti: str, user_id: str) -> None:
    """
    Сохраняем refresh token в Redis.

    key   = auth:refresh:<jti>
    value = user_id
    ttl   = refresh_token_expire_days
    """
    logger.debug(f"storing token: jti={jti}, user_id={user_id}")
    key = _refresh_key(jti)

    ttl = int(timedelta(days=settings.refresh_token_expire_days).total_seconds())

    logger.debug("Token is succesfully stored.")
    await redis_client.set(key, user_id, ex=ttl)


async def is_refresh_token_valid(jti: str) -> bool:
    key = _refresh_key(jti)

    value = await redis_client.get(key)

    return value is not None


async def revoke_refresh_token(jti: str) -> None:
    key = _refresh_key(jti)

    await redis_client.delete(key)


async def rotate_refresh_token(old_jti: str, new_jti: str, user_id: str):
    logger.debug(
        f"Rotating token: old_jti={old_jti}, new_jti={new_jti}, user_id={user_id}"
    )
    pipe = redis_client.pipeline()

    old_key = _refresh_key(old_jti)
    new_key = _refresh_key(new_jti)

    ttl = int(timedelta(days=settings.refresh_token_expire_days).total_seconds())

    pipe.delete(old_key)
    pipe.set(new_key, user_id, ex=ttl)

    logger.debug('Token is rotated.')
    await pipe.execute()
