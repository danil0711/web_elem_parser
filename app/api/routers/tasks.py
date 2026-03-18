from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.api.crud.schema import TaskBase, TaskCreate, TaskRead
from app.api.crud.task import (
    create_task,
    get_tasks,
    get_task_by_id,
    update_task,
    delete_task,
)
from app.core.logger import logger
from app.infrastructure.db.get_db import get_db
from app.api.deps.auth import get_current_user
from app.infrastructure.db.models.user import User
from app.infrastructure.fetchers.exception import FetcherError
from app.metrics.tasks import tasks_failed_total

router = APIRouter(prefix="/tasks", tags=["Tasks"])


# ---------- Создание задачи ----------
@router.post("/", response_model=TaskRead)
async def api_create_task(
    task_data: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        task = await create_task(db, user_id=current_user.id, task_data=task_data)
    except FetcherError as e:
        logger.error(f'failed create task: {e}')
        tasks_failed_total.inc() 
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )
    return task


# ---------- Получить все задачи пользователя ----------
@router.get("/", response_model=List[TaskRead])
async def api_get_tasks(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await get_tasks(db, user_id=current_user.id)


# ---------- Получить задачу по id ----------
@router.get("/{task_id}", response_model=TaskRead)
async def api_get_task_by_id(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = await get_task_by_id(db, task_id=task_id, user_id=current_user.id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    return task


# ---------- Обновить задачу ----------
@router.put("/{task_id}", response_model=TaskRead)
async def api_update_task(
    task_id: int,
    updates: TaskBase,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = await get_task_by_id(db, task_id=task_id, user_id=current_user.id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    try:

        updated_task = await update_task(db, task, updates)
    except FetcherError as e:
        logger.error(f'failed update task: {e}')
        tasks_failed_total.inc()
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )
    return updated_task


# ---------- Удалить задачу ----------
@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def api_delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = await get_task_by_id(db, task_id=task_id, user_id=current_user.id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    await delete_task(db, task)
    return
