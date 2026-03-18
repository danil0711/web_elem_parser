from prometheus_client import Counter
from prometheus_client import Gauge

tasks_created_total = Counter(
    "tasks_created_total",
    "Total number of created tasks",
)

tasks_failed_total = Counter(
    "tasks_failed_total",
    "Total number of failed tasks",
)

tasks_executed_total = Counter(
    "tasks_executed_total",
    "Total number of executed tasks",
)

tasks_ready_total = Gauge(
    "tasks_ready_total",
    "Tasks ready for execution",
)