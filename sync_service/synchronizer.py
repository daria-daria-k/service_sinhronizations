import logging
import os
import time
from sync_service.cloud.base import CloudStorage, CloudStorageError
from sync_service.local_scanner import collect_local_files


def diff(current_local: dict, previous_local: dict, remote_files: dict) -> tuple[set, set, set]:
    """Функция для определения действия с файлами (добавить, обновить, удалить)"""
    to_upload = set(current_local) - set(remote_files)
    to_delete = set(remote_files) - set(current_local)
    to_reload = set()

    for filename in set(current_local) & set(remote_files):
        if filename in previous_local and current_local[filename] != previous_local[filename]:
            to_reload.add(filename)

    return to_upload, to_delete, to_reload


def apply_changes(storage: CloudStorage,
                  local_path: str,
                  to_upload: set,
                  to_reload: set,
                  to_delete: set,
                  logger: logging.Logger) -> None:
    """Функция для применения изменений в облачном хранилище"""

    for filename in to_upload:
        try:
            storage.load(os.path.join(local_path, filename))
            logger.info(f"Загружен новый файл: {filename}")
        except (CloudStorageError, OSError) as e:
            logger.error(f"Не удалось загрузить файл {filename}: {e}")

    for filename in to_reload:
        try:
            storage.reload(os.path.join(local_path, filename))
            logger.info(f"Файл обновлен: {filename}")
        except (CloudStorageError, OSError) as e:
            logger.error(f"Не удалось обновить файл {filename}: {e}")

    for filename in to_delete:
        try:
            storage.delete(filename)
            logger.info(f"Файл удален: {filename}")
        except (CloudStorageError, OSError) as e:
            logger.error(f"Файл не удалось удалить {filename}: {e}")


def run_once(storage: CloudStorage, local_path: str, previous_local: dict, logger: logging.Logger) -> dict:
    """Функция выполняет один цикл синхронизации с облаком"""
    try:
        current_local = collect_local_files(local_path)
        remote_files = set(storage.get_info())
    except (CloudStorageError, OSError) as e:
        logger.error(f"Цикл синхронизации пропущен: {e}")
        return previous_local

    to_upload, to_delete, to_reload = diff(current_local, previous_local, remote_files)
    apply_changes(storage, local_path, to_upload, to_reload, to_delete, logger)
    return current_local


def run_forever(storage: CloudStorage, local_path: str, period: int, logger: logging.Logger) -> None:
    """Функция выполняет бесконечный цикл"""
    previous_local = {}
    while True:
        previous_local = run_once(storage, local_path, previous_local, logger)
        time.sleep(period)
