"""Настройка логгера для сервиса синхронизации."""

import logging


_LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logger(log_path: str) -> logging.Logger:
    """Создать и настроить логгер с записью в файл и в stdout.

    :param log_path: путь к файлу лога.
    :return: настроенный ``logging.Logger``.
    """
    logger = logging.getLogger("sync_service")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    formatter = logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT)
    logger.addHandler(_make_file_handler(log_path, formatter))
    logger.addHandler(_make_stream_handler(formatter))
    logger.propagate = False
    return logger


def _make_file_handler(
    log_path: str, formatter: logging.Formatter
) -> logging.Handler:
    """Создать файловый обработчик."""
    handler = logging.FileHandler(log_path, encoding="utf-8")
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)
    return handler


def _make_stream_handler(formatter: logging.Formatter) -> logging.Handler:
    """Создать обработчик для вывода в stdout."""
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)
    return handler
