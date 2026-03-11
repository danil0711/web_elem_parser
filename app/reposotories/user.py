from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.context import CryptContext

from app.core.security import hash_password, verify_password
from app.infrastructure.db.models.user import User


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()


async def create_user(db: AsyncSession, email: str, username: str, password: str):
    hashed_password = hash_password(password)

    db_user = User(username=username, email=email, hashed_password=hashed_password)

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def authenticate_user(db: AsyncSession, identifier: str, password: str):
    if "@" in identifier:
        stmt = select(User).where(User.email == identifier)
    else:
        stmt = select(User).where(User.username == identifier)

    result = await db.execute(stmt)

    user = result.scalars().first()

    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalars().first()


async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(User).where(User.username == username))

    return result.scalars().first()
