# app/api/auth.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.core.logger import logger
from app.reposotories.user import (
    authenticate_user,
    create_user,
    get_user_by_email,
    get_user_by_username,
)
from app.infrastructure.db.get_db import get_db
from app.schemas.user import UserCreate, Token
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import create_access_token


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=Token)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    logger.info(f"Register attempt: {user.email}")

    existing_email = await get_user_by_email(db, user.email)
    if existing_email:
        logger.warning(f"Register failed: email already exists ({user.email})")
        raise HTTPException(status_code=400, detail="Такой email уже зарегистрирован.")

    existing_username = await get_user_by_username(db, user.username)
    if existing_username:
        logger.warning(f"Register failed: username already exists ({user.email})")
        raise HTTPException(status_code=400, detail="Username уже занят.")

    try:
        db_user = await create_user(db, user.email, user.password, user.username)

        access_token = create_access_token({"sub": str(db_user.id)})
        logger.info(f"User registered successfully id={db_user.id}")

        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        logger.exception(f"Register failed due to internal error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    logger.info(f"Login attempt: {form_data.username}")

    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        logger.warning(f"Login failed: invalid credentials ({form_data.username})")
        raise HTTPException(status_code=401, detail="Неверный email или пароль")

    try:
        access_token = create_access_token({"sub": str(user.id)})
        logger.info(f"Login success: user_id={user.id}")
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception:
        logger.exception("Unexpected error while creating access token")
        raise HTTPException(status_code=500, detail="Internal server error")
