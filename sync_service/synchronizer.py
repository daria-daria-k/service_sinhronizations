"""Логика синхронизации локальной папки с облачным хранилищем."""

import logging
import os
import time
from typing import Dict, Set, Tuple

from sync_service.cloud.base import CloudStorage, CloudStorageError
from sync_service.local_scanner import collect_local_files


DiffResult = Tuple[Set[str], Set[str], Set[str]]


def diff(
    current_local: Dict[str, float],
    previous_local: Dict[str, float],
    remote_names: Set[str],
) -> DiffResult:
    """Вернуть три набора имён: ``to_upload``, ``to_reload``, ``to_delete``.

    :param current_local: текущая локальная карта ``{имя: mtime}``.
    :param previous_local: предыдущая локальная карта (пустая на первом запуске).
    :param remote_names: множество имён файлов, уже лежащих в облаке.
    """
    local_names = set(current_local)
    to_upload = local_names - remote_names
    to_delete = remote_names - local_names
    to_reload = _changed_files(current_local, previous_local, local_names & remote_names)
    return to_upload, to_reload, to_delete


def _changed_files(
    current: Dict[str, float],
    previous: Dict[str, float],
    common: Set[str],
) -> Set[str]:
    """Вернуть имена общих файлов, у которых изменилось ``mtime``."""
    return {name for name in common if _mtime_changed(name, current, previous)}


def _mtime_changed(
    name: str, current: Dict[str, float], previous: Dict[str, float]
) -> bool:
    """Проверить, видели ли мы файл раньше с другим временем изменения."""
    return name in previous and previous[name] != current[name]


def apply_changes(
    storage: CloudStorage,
    local_path: str,
    to_upload: Set[str],
    to_reload: Set[str],
    to_delete: Set[str],
    logger: logging.Logger,
) -> None:
    """Применить изменения в облаке. Ошибки по конкретному файлу логируются."""
    _apply_uploads(storage, local_path, to_upload, logger)
    _apply_reloads(storage, local_path, to_reload, logger)
    _apply_deletes(storage, to_delete, logger)


def _apply_uploads(storage, local_path, names, logger):
    """Загрузить новые файлы."""
    for name in names:
        _safe_call(
            lambda: storage.load(os.path.join(local_path, name)),
            success=f"Загружен новый файл: {name}",
            failure=f"Не удалось загрузить файл {name}",
            logger=logger,
        )


def _apply_reloads(storage, local_path, names, logger):
    """Перезаписать изменённые файлы."""
    for name in names:
        _safe_call(
            lambda: storage.reload(os.path.join(local_path, name)),
            success=f"Обновлён файл: {name}",
            failure=f"Не удалось обновить файл {name}",
            logger=logger,
        )


def _apply_deletes(storage, names, logger):
    """Удалить файлы, которых больше нет локально."""
    for name in names:
        _safe_call(
            lambda: storage.delete(name),
            success=f"Удалён файл: {name}",
            failure=f"Не удалось удалить файл {name}",
            logger=logger,
        )


def _safe_call(action, success, failure, logger):
    """Выполнить действие, перехватывая ошибки и записывая результат в лог."""
    try:
        action()
    except (CloudStorageError, OSError) as exc:
        logger.error("%s: %s", failure, exc)
        return
    logger.info(success)


def run_once(
    storage: CloudStorage,
    local_path: str,
    previous_local: Dict[str, float],
    logger: logging.Logger,
) -> Dict[str, float]:
    """Выполнить один цикл синхронизации и вернуть актуальную карту локальных файлов."""
    try:
        current_local = collect_local_files(local_path)
        remote = set(storage.get_info())
    except (CloudStorageError, OSError) as exc:
        logger.error("Цикл синхронизации пропущен: %s", exc)
        return previous_local
    to_upload, to_reload, to_delete = diff(current_local, previous_local, remote)
    apply_changes(
        storage, local_path, to_upload, to_reload, to_delete, logger
    )
    return current_local


def run_forever(
    storage: CloudStorage,
    local_path: str,
    period: int,
    logger: logging.Logger,
    sleep=time.sleep,
) -> None:
    """Запустить бесконечный цикл синхронизации с шагом ``period`` секунд."""
    state: Dict[str, float] = {}
    while True:
        state = run_once(storage, local_path, state, logger)
        sleep(period)
