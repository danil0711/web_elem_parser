import asyncio
from datetime import datetime, timezone
from select import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.models.task import Task
from app.services.monitoring.monitoring import run_task


async def orchestrator_loop(db: AsyncSession):
    """
    Минимальный рабочий loop, имитирующий Beat.
    """
    while True:
        now = datetime.now(timezone.utc)
        result = await db.execute(select(Task).where(Task.is_active))
        tasks = result.scalars().all()

        for task in tasks:
            if task.is_due(now):
                await run_task(db, task)
                task.last_run_at = datetime.now(timezone.utc)
                db.add(task)

        await db.commit()
        await asyncio.sleep(10)