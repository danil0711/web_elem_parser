from datetime import datetime, UTC
from app.infrastructure.db.models.task import Task
from app.infrastructure.fetchers.async_fetcher import fetcher
from app.services.condition.condition import ConditionEvaluator
from app.services.parser.parser import ParserService


# TODO при хендле ошибки отключать задачу.
async def run_task(task: Task):
    html = await fetcher.fetch(task.url)
    parser = ParserService()

    html = await fetcher.fetch(task.url)
    # получаем значение с сайта по селектору
    extracted_value = parser.extract_text(html, task.selector)

    should_alert = False

    if task.condition:
        should_alert = ConditionEvaluator.check_condition(
            task.condition, extracted_value
        )

    if should_alert:
        print(f"ALERT for task {task.id}")

    task.last_run_at = datetime.now(UTC)
