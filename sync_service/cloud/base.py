from abc import ABC, abstractmethod


class CloudStorageError(Exception):
    """Класс для идентификации ошибок, связанных с работой хранилища"""
    pass


class CloudAuthError(CloudStorageError):
    """Класс для идентификации ошибок, связанных с авторизацией хранилища"""
    pass


class CloudStorage(ABC):
    """Абстрактный интерфейс для облачного хранилища"""

    @abstractmethod
    def load(self, path: str) -> None:
        """Загрузить новый файл в хранилище"""

    @abstractmethod
    def reload(self, path: str) -> None:
        """Перезаписать файл в хранилище"""

    @abstractmethod
    def delete(self, path: str) -> None:
        """Удалить файл из хранилища"""

    @abstractmethod
    def get_info(self) -> dict[str, str]:
        """Вернуть словарь {имя_файла: время_изменения} из хранилища."""
