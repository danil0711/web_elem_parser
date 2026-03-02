from datetime import datetime, timedelta, timezone
from jose import jwt
from app.infrastructure.config import settings
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )

    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm,
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