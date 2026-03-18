from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.crud.schema import TaskBase, TaskCreate
from app.core.logger import logger
from app.infrastructure.db.models.task import Task


async def create_task(db: AsyncSession, user_id: int, task_data: TaskCreate) -> Task:
    data = task_data.model_dump()

    logger.info(f"Создаём задачу для user_id={user_id} с данными: {data}")

    data["url"] = str(data["url"])  # <--- конвертируем HttpUrl → str

    task = Task(user_id=user_id, next_run_at=datetime.now(timezone.utc), **data)

    db.add(task)

    await db.commit()
    await db.refresh(task)

    logger.info(f"Задача создана с id={task.id}")
    return task


async def get_tasks(db: AsyncSession, user_id: int):
    logger.debug(f"Получаем все задачи для user_id={user_id}")
    result = await db.execute(
        select(Task).where(Task.user_id == user_id).order_by(Task.created_at.desc())
    )
    tasks = result.scalars().all()
    logger.debug(f"Найдено {len(tasks)} задач(и) для user_id={user_id}")
    return tasks


async def get_task_by_id(db: AsyncSession, task_id: int, user_id: int):
    logger.info(f"Получаем задачу id={task_id} для user_id={user_id}")
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    )
    task = result.scalar_one_or_none()
    if task:
        logger.info(f"Задача найдена: id={task.id}")
    else:
        logger.warning(f"Задача id={task_id} для user_id={user_id} не найдена")
    return task


async def update_task(db: AsyncSession, task: Task, updates: TaskBase) -> Task:
    update_data = updates.model_dump(exclude_unset=True)
    logger.info(f"Обновляем задачу id={task.id} с данными: {update_data}")
    if "url" in update_data:
        update_data["url"] = str(update_data["url"])
    if "interval" in update_data:
        task.schedule_next_run()
    for key, value in update_data.items():
        setattr(task, key, value)
    db.add(task)
    await db.commit()
    await db.refresh(task)
    logger.info(f"Задача id={task.id} обновлена")
    return task


async def delete_task(db: AsyncSession, task: Task):
    logger.info(f"Удаляем задачу id={task.id} для user_id={task.user_id}")
    await db.delete(task)
    await db.commit()
    logger.info(f"Задача id={task.id} удалена")
