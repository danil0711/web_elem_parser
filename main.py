import os
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.core.logger import logger
from app.api.auth import router as auth_router
from app.infrastructure.db.health import check_db_connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not await check_db_connection():
        logger.critical("Cannot connect to database. Exiting.")
        os._exit(1)

    yield
    logger.info("Application shutdown")


app = FastAPI(lifespan=lifespan)
app.include_router(auth_router)
