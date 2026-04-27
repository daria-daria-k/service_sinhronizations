"""Сканер локальной папки.

Согласно ТЗ в синхронизируемой папке появляются только файлы,
вложенные папки не учитываются.
"""

import os
from typing import Dict


def collect_local_files(local_path: str) -> Dict[str, float]:
    """Вернуть словарь ``{имя_файла: mtime}`` для файлов в ``local_path``.

    :param local_path: путь к синхронизируемой папке.
    :return: словарь имён файлов и времени их последнего изменения.
    """
    entries = os.listdir(local_path)
    return dict(_iter_file_entries(local_path, entries))


def _iter_file_entries(local_path: str, entries):
    """Вернуть пары ``(имя_файла, mtime)`` только для обычных файлов."""
    for name in entries:
        full = os.path.join(local_path, name)
        if os.path.isfile(full):
            yield name, os.path.getmtime(full)
