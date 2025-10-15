import logging
import logging.handlers
import os
from pathlib import Path


def setup_logging():
    """Настройка системы логирования"""

    # Создаем директорию для логов
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Основной логгер
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Форматтер для логов
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )

    # Файловый хендлер с ротацией
    file_handler = logging.handlers.RotatingFileHandler(
        log_dir / 'bot.log',
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # Консольный хендлер
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO if os.getenv('DEBUG') else logging.WARNING)
    console_handler.setFormatter(formatter)

    # Добавляем хендлеры
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # Отдельный логгер для ошибок
    error_handler = logging.FileHandler(
        log_dir / 'errors.log',
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)

    return logger