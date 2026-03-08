import os
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from app.core.logger import logger
from app.api.routers.auth import router as auth_router
from app.api.routers.users import router as users_router
from app.api.routers.tasks import router as tasks_router
from app.infrastructure.db.health import check_db_connection
from app.services.scheduler.scheduler import start_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not await check_db_connection():
        logger.critical("Cannot connect to database. Exiting.")
        os._exit(1)

    logger.info("Starting scheduler")
    start_scheduler()

    yield

    logger.info("Application shutdown")


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(tasks_router)
