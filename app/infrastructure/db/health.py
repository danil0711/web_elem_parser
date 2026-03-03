from asyncpg import CannotConnectNowError, InvalidPasswordError
from sqlalchemy import text
from sqlalchemy.exc import OperationalError


from app.core.logger import logger
from app.infrastructure.db.get_db import get_db


async def check_db_connection() -> bool:
    """Проверка соединения с базой. Возвращает True, если ОК, иначе False"""
    try:
        async for session in get_db():
            await session.execute(text("SELECT 1"))
            return True
    except (OperationalError, InvalidPasswordError, CannotConnectNowError) as e:
        logger.error(f"❌ Database connection error: {e.__class__.__name__} - {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected database error: {e}")
        return False