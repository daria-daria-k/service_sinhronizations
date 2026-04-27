"""Точка входа сервиса синхронизации."""

import sys

from sync_service.cloud.base import CloudAuthError, CloudStorageError
from sync_service.cloud.yandex_disk import YandexDisk
from sync_service.config_loader import Config, ConfigError, load_config
from sync_service.logger import setup_logger
from sync_service.synchronizer import run_forever


CONFIG_PATH = "config.ini"


def main() -> int:
    """Запустить сервис. Возвращает код выхода."""
    config = _load_or_exit()
    logger = setup_logger(config.log_path)
    logger.info(
        "Программа запущена. Синхронизируемая папка: %s", config.local_path
    )
    storage = _build_storage_or_exit(config, logger)
    try:
        run_forever(storage, config.local_path, config.period, logger)
    except KeyboardInterrupt:
        logger.info("Программа остановлена пользователем.")
        return 0
    return 0


def _load_or_exit() -> Config:
    """Прочитать конфиг, при ошибке — печатать сообщение и выйти."""
    try:
        return load_config(CONFIG_PATH)
    except ConfigError as exc:
        print(f"Ошибка конфигурации: {exc}", file=sys.stderr)
        sys.exit(1)


def _build_storage_or_exit(config: Config, logger) -> YandexDisk:
    """Создать клиент Яндекс.Диска, при ошибке доступа — выйти."""
    try:
        return YandexDisk(config.token, config.remote_name)
    except CloudAuthError as exc:
        logger.error("Ошибка авторизации: %s", exc)
        print(f"Ошибка авторизации: {exc}", file=sys.stderr)
        sys.exit(1)
    except CloudStorageError as exc:
        logger.error("Ошибка облачного хранилища: %s", exc)
        print(f"Ошибка облачного хранилища: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    raise SystemExit(main())
