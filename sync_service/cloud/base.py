"""Базовый интерфейс облачного хранилища.

Любая новая реализация (Google Drive, Dropbox и т. д.) должна наследовать
``CloudStorage`` и предоставлять четыре публичных метода: ``load``,
``reload``, ``delete``, ``get_info``.
"""

from abc import ABC, abstractmethod
from typing import Dict


class CloudStorageError(Exception):
    """Базовый класс ошибок при работе с облачным хранилищем."""


class CloudAuthError(CloudStorageError):
    """Невалидный токен или нет доступа к удалённой папке."""


class CloudStorage(ABC):
    """Абстрактный интерфейс облачного хранилища."""

    @abstractmethod
    def load(self, path: str) -> None:
        """Загрузить новый файл по локальному пути ``path`` в хранилище."""

    @abstractmethod
    def reload(self, path: str) -> None:
        """Перезаписать файл по локальному пути ``path`` в хранилище."""

    @abstractmethod
    def delete(self, filename: str) -> None:
        """Удалить файл с именем ``filename`` из удалённой папки."""

    @abstractmethod
    def get_info(self) -> Dict[str, str]:
        """Вернуть словарь ``{имя_файла: время_изменения_iso}``."""
