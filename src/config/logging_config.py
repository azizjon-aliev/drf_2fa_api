from loguru import logger
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
LOG_FILE = BASE_DIR / 'logs' / 'login_attempts.log'

# Создадим каталог для логов, если не существует
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

logger.add(
	LOG_FILE,
	rotation="1 week",  # раз в неделю новый файл
	retention="1 months",  # хранить логи за месяц
	level="INFO",
	format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)
