import asyncio
from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import logger
from app.infrastructure.db.models.task import Task
from app.infrastructure.db.session import AsyncSessionLocal
from app.infrastructure.fetchers.exception import ClientError, SSLError
from app.services.monitoring.monitoring import run_task


scheduler = AsyncIOScheduler()

semaphore = asyncio.Semaphore(20)


async def execute_task(task_id: int) -> None:
    start_time = datetime.now(timezone.utc)

    async with AsyncSessionLocal() as db:
        try:
            task = await db.get(Task, task_id)

            if not task or not task.is_active:
                logger.debug(f"Task {task_id} skipped")
                return

            logger.info(f"Task {task.id} started")

            await run_task(task)

            task.schedule_next_run()

            await db.commit()

            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            logger.info(f"Task {task.id} finished in {duration:.2f}s")

        except SSLError:
            await handle_close_task_due_critical_error(
                db,
                task_id,
                "SSL error",
            )

        except ClientError:
            await handle_close_task_due_critical_error(
                db,
                task_id,
                "401 Unauthorized",
            )

        except Exception:
            await db.rollback()
            logger.exception(f"Task {task_id} execution failed")


async def handle_close_task_due_critical_error(
    db: AsyncSession,
    task_id: int,
    reason: str,
) -> None:
    await db.rollback()

    task = await db.get(Task, task_id)
    if not task:
        return

    if not task.is_active:
        return

    task.is_active = False
    await db.commit()

    logger.error(f"Task {task_id} disabled: {reason}")


async def check_tasks() -> None:
    tick_start = datetime.now(timezone.utc)
    logger.debug("Scheduler tick started")
    async with AsyncSessionLocal() as db:
        now = datetime.now(timezone.utc)

        result = await db.execute(
            select(Task)
            .where(
                Task.is_active.is_(True),
                Task.next_run_at <= now,
            )
            .limit(500)
            .with_for_update(skip_locked=True)
        )

        tasks = result.scalars().all()

        if not tasks:
            logger.debug("Scheduler tick: no tasks ready")
            return

        logger.info(f"Scheduler fetched {len(tasks)} tasks")

        for task in tasks:
            logger.debug(f"Queueing task {task.id}")
            asyncio.create_task(run_with_limit(task.id))

        duration = (datetime.now(timezone.utc) - tick_start).total_seconds()
        logger.debug(f"Scheduler tick finished in {duration:.2f}s")


async def run_with_limit(task_id: int):
    logger.debug(f"Waiting semaphore for task {task_id}")
    async with semaphore:
        logger.debug(f"Semaphore acquired for task {task_id}")
        await execute_task(task_id)


def start_scheduler() -> None:

    logger.info("Scheduler started")

    logger.info("Scheduler config: interval=5s, limit=500, concurrency=20")

    scheduler.add_job(
        check_tasks,
        IntervalTrigger(seconds=5),
        max_instances=1,
        next_run_time=datetime.now(timezone.utc),
    )

    scheduler.start()
