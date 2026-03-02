from app.api.auth import router as auth_router
from fastapi import FastAPI

from app.core.logger import logger

app = FastAPI()
logger.info('Application starting', app)
app.include_router(auth_router)


# uvicorn main:app --reload --log-level debug