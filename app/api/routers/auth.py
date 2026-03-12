# app/api/auth.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.core.logger import logger
from app.infrastructure.cache.redis_cache import (
    is_refresh_token_valid,
    revoke_refresh_token,
    rotate_refresh_token,
    store_refresh_token,
)
from app.reposotories.user import (
    authenticate_user,
    create_user,
    get_user_by_email,
    get_user_by_username,
)
from app.infrastructure.db.get_db import get_db
from app.schemas.user import RefreshRequest, UserCreate, Token
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
)


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
        refresh_token, jti = create_refresh_token({"sub": str(user.id)})

        await store_refresh_token(jti, str(user.id))

        logger.success(f"Login success: user_id={user.id}")
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
    except Exception:
        logger.exception("Unexpected error while creating access token")
        raise HTTPException(status_code=500, detail="Internal server error")
    

@router.post("/logout")
async def logout(data: RefreshRequest):
    payload = verify_refresh_token(data.refresh_token)

    jti = payload.get("jti")

    logger.debug(f'Logouting and revoking jti={jti}')

    if not jti:
        raise HTTPException(status_code=401, detail="Invalid token")

    await revoke_refresh_token(jti)

    return {"message": "Logged out"}


@router.post("/refresh")
async def refresh_token(data: RefreshRequest):
    logger.debug("token refreshing")
    payload = verify_refresh_token(data.refresh_token)

    user_id = payload.get("sub")
    jti = payload.get("jti")

    if not user_id or jti:
        raise HTTPException(status_code=401, detail="Invalid token")

    valid = await is_refresh_token_valid(jti)

    if not valid:
        raise HTTPException(status_code=401, detail="Refresh token revoked")

    new_access_token = create_access_token({"sub": user_id})
    new_refresh_token, new_jti = create_refresh_token({"sub": user_id})

    await rotate_refresh_token(jti, new_jti, user_id)

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


