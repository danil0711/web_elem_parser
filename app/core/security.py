from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from jose import JWTError, jwt
from app.core.logger import logger
from app.infrastructure.config import settings
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )

    to_encode.update({"exp": expire, "type": "access"})

    logger.debug(
        f"Creating access token: user_id={data.get('sub')} exp={expire.isoformat()}"
    )

    return jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm,
    )


def create_refresh_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.refresh_token_expire_days
    )

    logger.debug(
        f"Creating refresh token: user_id={data.get('sub')} exp={expire.isoformat()}"
    )

    to_encode.update({"exp": expire, "type": "refresh"})

    return jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm,
    )

def verify_access_token(token: str) -> dict:
    logger.debug("Access token verification attempt")
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )

        token_type = payload.get("type")
        if token_type != "access":
            logger.warning(f"Invalid token type: expected=access got={token_type}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type"
            )

        logger.debug(
            f"Access token verified: user_id={payload.get('sub')} exp={payload.get('exp')}"
        )

        return payload

    except JWTError as e:
        logger.warning(f"Acess token validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )


def verify_refresh_token(token: str) -> dict:
    logger.debug("verify_refresh_token")
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )

        token_type = payload.get("type")
        if token_type != "refresh":
            logger.warning(f"Invalid token type: expected=refresh got={token_type}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type"
            )
        logger.debug(
            f"Refresh token verified: user_id={payload.get('sub')} exp={payload.get('exp')}"
        )
        return payload

    except JWTError as e:
        logger.warning(f"Refresh token validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )


def hash_password(password: str) -> str:
    """
    Хешируем пароль через Argon2
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяем пароль через Argon2
    """
    return pwd_context.verify(plain_password, hashed_password)

