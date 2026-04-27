"""Реализация ``CloudStorage`` для Яндекс.Диска.

Используется REST API ``https://cloud-api.yandex.net/v1/disk/resources``.
Единственная сторонняя зависимость — ``requests``.
"""

import os
from typing import Dict

import requests

from sync_service.cloud.base import (
    CloudAuthError,
    CloudStorage,
    CloudStorageError,
)


_API_BASE = "https://cloud-api.yandex.net/v1/disk"
_REQUEST_TIMEOUT = 30


def _build_remote_path(remote_dir: str, filename: str) -> str:
    """Склеить путь к файлу в удалённой папке."""
    return f"{remote_dir.rstrip('/')}/{filename}"


class YandexDisk(CloudStorage):
    """Хранилище на основе Яндекс.Диска."""

    def __init__(self, token: str, remote_path: str) -> None:
        """Сохранить токен и удалённую папку, проверить доступ.

        :param token: OAuth-токен с правами на Яндекс.Диск.
        :param remote_path: имя/путь удалённой папки для бэкапа.
        :raises CloudAuthError: при невалидном токене.
        """
        self._token = token
        self._remote_path = remote_path
        self._headers = {"Authorization": f"OAuth {token}"}
        self._verify_token()
        self._ensure_remote_folder()

    def load(self, path: str) -> None:
        """Загрузить новый файл (без перезаписи)."""
        self._upload(path, overwrite=False)

    def reload(self, path: str) -> None:
        """Перезаписать существующий файл."""
        self._upload(path, overwrite=True)

    def delete(self, filename: str) -> None:
        """Удалить файл по имени из удалённой папки."""
        remote = _build_remote_path(self._remote_path, filename)
        url = f"{_API_BASE}/resources"
        params = {"path": remote, "permanently": "true"}
        response = requests.delete(
            url, headers=self._headers, params=params, timeout=_REQUEST_TIMEOUT
        )
        self._raise_for_status(response, f"Не удалось удалить '{filename}'")

    def get_info(self) -> Dict[str, str]:
        """Получить словарь ``{имя_файла: modified}`` из удалённой папки."""
        url = f"{_API_BASE}/resources"
        params = {
            "path": self._remote_path,
            "fields": "_embedded.items.name,_embedded.items.modified",
            "limit": 1000,
        }
        response = requests.get(
            url, headers=self._headers, params=params, timeout=_REQUEST_TIMEOUT
        )
        self._raise_for_status(response, "Не удалось получить список файлов")
        items = response.json().get("_embedded", {}).get("items", [])
        return {item["name"]: item["modified"] for item in items}

    # --- внутренние помощники -----------------------------------------

    def _verify_token(self) -> None:
        """Проверить токен через ``GET /v1/disk/``."""
        response = requests.get(
            f"{_API_BASE}/", headers=self._headers, timeout=_REQUEST_TIMEOUT
        )
        if response.status_code == 401:
            raise CloudAuthError(
                "Неверный или просроченный токен Яндекс.Диска."
            )
        self._raise_for_status(response, "Не удалось подключиться к Яндекс.Диску")

    def _ensure_remote_folder(self) -> None:
        """Создать удалённую папку, если её ещё нет."""
        url = f"{_API_BASE}/resources"
        params = {"path": self._remote_path}
        response = requests.put(
            url, headers=self._headers, params=params, timeout=_REQUEST_TIMEOUT
        )
        if response.status_code in (201, 409):
            return
        self._raise_for_status(
            response, f"Не удалось создать удалённую папку '{self._remote_path}'"
        )

    def _upload(self, local_path: str, overwrite: bool) -> None:
        """Залить файл по полученному upload URL."""
        upload_url = self._request_upload_url(local_path, overwrite)
        self._put_file(upload_url, local_path)

    def _request_upload_url(self, local_path: str, overwrite: bool) -> str:
        """Запросить у API одноразовый URL для загрузки."""
        filename = os.path.basename(local_path)
        remote = _build_remote_path(self._remote_path, filename)
        url = f"{_API_BASE}/resources/upload"
        params = {"path": remote, "overwrite": str(overwrite).lower()}
        response = requests.get(
            url, headers=self._headers, params=params, timeout=_REQUEST_TIMEOUT
        )
        self._raise_for_status(
            response, f"Не удалось получить upload URL для '{filename}'"
        )
        return response.json()["href"]

    def _put_file(self, upload_url: str, local_path: str) -> None:
        """Передать содержимое файла по полученному URL."""
        with open(local_path, "rb") as fileobj:
            response = requests.put(
                upload_url, data=fileobj, timeout=_REQUEST_TIMEOUT
            )
        if response.status_code not in (200, 201, 202):
            raise CloudStorageError(
                f"Загрузка файла '{local_path}' завершилась с кодом "
                f"{response.status_code}"
            )

    @staticmethod
    def _raise_for_status(response: requests.Response, message: str) -> None:
        """Поднять ``CloudStorageError`` для не-2xx ответов."""
        if response.status_code < 400:
            return
        raise CloudStorageError(
            f"{message}: HTTP {response.status_code} — {response.text[:200]}"
        )
