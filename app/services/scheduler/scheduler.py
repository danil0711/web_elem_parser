import asyncio
from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import select

from app.core.logger import logger
from app.infrastructure.db.models.task import Task
from app.infrastructure.db.session import AsyncSessionLocal
from app.services.monitoring.monitoring import run_task


scheduler = AsyncIOScheduler()


async def execute_task(task_id: int) -> None:
    async with AsyncSessionLocal() as db:
        task = await db.get(Task, task_id)

        if not task or not task.is_active:
            return

        try:
            await run_task(db, task)

            task.last_run_at = datetime.now(timezone.utc)

            await db.commit()

        except Exception:
            await db.rollback()

            logger.exception("Task execution failed")


async def check_tasks() -> None:
    """
    Проверяет задачи и запускает те, которые должны выполниться.
    """


    async with AsyncSessionLocal() as db:
        now = datetime.now(timezone.utc)

        result = await db.execute(select(Task).where(Task.is_active))

        tasks = result.scalars().all()


        to_run = []

        for task in tasks:
            if task.should_run(now):
                to_run.append(task.id)

        logger.info(
            f"Tasks to run: {len(to_run)}",
        )

        for task_id in to_run:
            asyncio.create_task(execute_task(task_id))


def start_scheduler() -> None:

    logger.info("Scheduler started")

    scheduler.add_job(
        check_tasks,
        IntervalTrigger(minutes=1),
        max_instances=1,
        next_run_time=datetime.now(timezone.utc)
    )

    scheduler.start()
