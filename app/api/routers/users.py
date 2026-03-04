from fastapi import APIRouter, Depends
from app.api.deps.auth import get_current_user
from app.infrastructure.db.models.user import User

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me")
async def read_me(current_user: User = Depends(get_current_user)):
    return current_user