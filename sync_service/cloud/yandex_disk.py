import os
import requests
from sync_service.cloud.base import CloudStorage, CloudStorageError, CloudAuthError

API_BASE = 'https://cloud-api.yandex.net/v1/disk'
TIMEOUT = 30


class YandexDisk(CloudStorage):
    """Реализация CloudStorage для Яндекс.Диска."""

    def __init__(self, token: str, remote_path: str) -> None:
        self._token = token
        self._remote_path = remote_path
        self._headers = {"Authorization": f"OAuth {token}"}

        self._verify_token()
        self._ensure_remote_folder()

    def _verify_token(self) -> None:
        """Функция проверка валидности токена"""
        response = requests.get(
            f"{API_BASE}/",
            headers=self._headers,
            timeout=TIMEOUT,
        )

        if response.status_code == 401:
            raise CloudAuthError("Неверный или просроченный токен")

    def _ensure_remote_folder(self) -> None:
        """Создать папку на Яндекс.Диске если её нет."""
        response = requests.put(
            f"{API_BASE}/resources",
            headers=self._headers,
            params={"path": self._remote_path},
            timeout=TIMEOUT,
        )

        if response.status_code not in (201, 409):
            raise CloudStorageError(f"Не удалось создать папку: {response.text}")

    def get_info(self) -> dict[str, str]:
        """Вернуть словарь {имя_файла: время_изменения} из удалённой папки."""

        response = requests.get(
            f"{API_BASE}/resources",
            headers=self._headers,
            params={"path": self._remote_path},
            timeout=TIMEOUT,
        )

        if response.status_code != 200:
            raise CloudStorageError(f"Не удалось получить список файлов: {response.text}")

        items = response.json()["_embedded"]["items"]
        return {item["name"]: item["modified"] for item in items}

    def _get_upload_url(self, filename: str, overwrite: bool) -> str:
        """Получить URL для загрузки файла."""
        response = requests.get(
            f"{API_BASE}/resources/upload",
            headers=self._headers,
            params={
                "path": f"{self._remote_path}/{filename}",
                "overwrite": overwrite,
            },
            timeout=TIMEOUT,
        )

        if response.status_code != 200:
            raise CloudStorageError(f"Не удалось получить URL для загрузки: {response.text}")

        return response.json()["href"]

    def _upload_file(self, upload_url: str, path: str) -> None:
        """Загрузить файл по указанному URL."""
        with open(path, "rb") as f:
            response = requests.put(
                upload_url,
                data=f,
                timeout=TIMEOUT,
            )

            if response.status_code not in (200, 201, 202):
                raise CloudStorageError(f"Не удалось загрузить файл: {response.text}")

    def load(self, path: str) -> None:
        """Загрузить новый файл в хранилище."""
        file = os.path.basename(path)
        upload_url = self._get_upload_url(file, False)
        self._upload_file(upload_url, path)

    def reload(self, path: str) -> None:
        """Перезаписать файл в хранилище."""
        file = os.path.basename(path)
        upload_url = self._get_upload_url(file, True)
        self._upload_file(upload_url, path)

    def delete(self, filename: str) -> None:
        """Удалить файл из хранилища."""
        response = requests.delete(
            f"{API_BASE}/resources",
            headers=self._headers,
            params={
                "path": f"{self._remote_path}/{filename}",
                "permanently": "true",
            },
            timeout=TIMEOUT,
        )

        if response.status_code != 204:
            raise CloudStorageError(f"Не удалось удалить файл: {response.text}")
