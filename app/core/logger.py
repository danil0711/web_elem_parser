from loguru import logger
import sys
import logging
from pathlib import Path

# Удаляем стандартный логгер loguru (на всякий случай)
logger.remove()

Path("logs").mkdir(parents=True, exist_ok=True)

# Добавляем логирование в консоль
# logger.add(sys.stdout, level="INFO")


# Отключаем DEBUG в продакшне
# if PROD:
#     console_level = "INFO"
# else:
#     console_level = "DEBUG"

console_level = "DEBUG"
    
logger.add(sys.stdout, level=console_level)

# Добавляем логирование в файл с ротацией по дням
logger.add(
    "logs/logs.file_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
    level="INFO",
    rotation="00:00",        # Ротация в полночь
    compression="zip",       # Сжатие архивных логов
    enqueue=True,            # Безопасно при многопоточности
    retention="30 days"      # Удаление старых логов
)

# Перенаправляем стандартный logging в loguru
class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Переводим уровень из logging в loguru
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        logger.opt(depth=6, exception=record.exc_info).log(level, record.getMessage())

# Подключаем перехватчик
logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO)
