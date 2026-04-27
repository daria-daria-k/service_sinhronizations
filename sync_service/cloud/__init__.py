"""Реализации облачных хранилищ для сервиса синхронизации."""

from sync_service.cloud.base import CloudStorage, CloudStorageError
from sync_service.cloud.yandex_disk import YandexDisk

__all__ = ["CloudStorage", "CloudStorageError", "YandexDisk"]
