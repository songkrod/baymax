import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from config.settings import settings

LOG_DIR = Path(settings.LOG_DIR)
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / settings.LOG_FILE

logger = logging.getLogger("Baymax")
logger.setLevel(getattr(logging, settings.LOG_LEVEL, logging.INFO))

file_handler = RotatingFileHandler(
    LOG_FILE,
    maxBytes=settings.LOG_FILE_SIZE_MB * 1024 * 1024,
    backupCount=settings.LOG_BACKUP_COUNT,
    encoding="utf-8"
)
file_handler.setLevel(getattr(logging, settings.LOG_LEVEL, logging.INFO))

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)