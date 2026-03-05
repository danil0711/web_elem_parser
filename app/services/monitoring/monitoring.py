from datetime import datetime, UTC
from app.infrastructure.db.models.task import Task
from app.infrastructure.fetchers.async_fetcher import HttpxAsyncFetcher
from app.services.condition.condition import ConditionEvaluator
from app.services.parser import ParserService
from sqlalchemy.ext.asyncio import AsyncSession

async def run_task(db: AsyncSession, task: Task):
    fetcher = HttpxAsyncFetcher()
    parser = ParserService()

    html = await fetcher.fetch(task.url)
    extracted_value = parser.extract_text(html, task.selector)

    should_alert = False

    if task.condition:
        should_alert = ConditionEvaluator.check_condition(task.condition, extracted_value)

    if should_alert:
        print(f"ALERT for task {task.id}")

    task.last_run_at = datetime.now(UTC)