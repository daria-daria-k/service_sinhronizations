"""Тесты для ``YandexDisk`` с mock-ами на ``requests``."""

import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from sync_service.cloud.base import CloudAuthError, CloudStorageError
from sync_service.cloud.yandex_disk import YandexDisk


def _ok(json_body=None, status=200):
    response = MagicMock()
    response.status_code = status
    response.json.return_value = json_body or {}
    response.text = ""
    return response


def _make_disk(mock_get, mock_put):
    """Создать YandexDisk с заранее замоканной валидацией."""
    mock_get.return_value = _ok({"user": {"login": "x"}})
    mock_put.return_value = _ok(status=201)
    return YandexDisk("token-123", "backup")


class YandexDiskInitTests(unittest.TestCase):
    """Поведение конструктора."""

    @patch("sync_service.cloud.yandex_disk.requests.put")
    @patch("sync_service.cloud.yandex_disk.requests.get")
    def test_invalid_token_raises_auth_error(self, mock_get, mock_put):
        mock_get.return_value = _ok(status=401)
        with self.assertRaises(CloudAuthError):
            YandexDisk("bad-token", "backup")

    @patch("sync_service.cloud.yandex_disk.requests.put")
    @patch("sync_service.cloud.yandex_disk.requests.get")
    def test_existing_folder_does_not_raise(self, mock_get, mock_put):
        mock_get.return_value = _ok({"user": {}})
        mock_put.return_value = _ok(status=409)
        disk = YandexDisk("token", "backup")
        self.assertIsInstance(disk, YandexDisk)

    @patch("sync_service.cloud.yandex_disk.requests.put")
    @patch("sync_service.cloud.yandex_disk.requests.get")
    def test_folder_create_failure_raises(self, mock_get, mock_put):
        mock_get.return_value = _ok({"user": {}})
        mock_put.return_value = _ok(status=500)
        with self.assertRaises(CloudStorageError):
            YandexDisk("token", "backup")


class YandexDiskMethodsTests(unittest.TestCase):
    """Тесты публичных методов ``YandexDisk``."""

    @patch("sync_service.cloud.yandex_disk.requests.delete")
    @patch("sync_service.cloud.yandex_disk.requests.put")
    @patch("sync_service.cloud.yandex_disk.requests.get")
    def test_delete_calls_api(self, mock_get, mock_put, mock_delete):
        disk = _make_disk(mock_get, mock_put)
        mock_delete.return_value = _ok(status=204)
        disk.delete("a.txt")
        args, kwargs = mock_delete.call_args
        self.assertIn("/v1/disk/resources", args[0])
        self.assertEqual(kwargs["params"]["path"], "backup/a.txt")
        self.assertEqual(kwargs["params"]["permanently"], "true")

    @patch("sync_service.cloud.yandex_disk.requests.put")
    @patch("sync_service.cloud.yandex_disk.requests.get")
    def test_get_info_returns_name_to_modified_map(self, mock_get, mock_put):
        disk = _make_disk(mock_get, mock_put)
        mock_get.return_value = _ok(
            {
                "_embedded": {
                    "items": [
                        {"name": "a.txt", "modified": "2025-01-01T00:00:00Z"},
                        {"name": "b.txt", "modified": "2025-01-02T00:00:00Z"},
                    ]
                }
            }
        )
        info = disk.get_info()
        self.assertEqual(
            info,
            {
                "a.txt": "2025-01-01T00:00:00Z",
                "b.txt": "2025-01-02T00:00:00Z",
            },
        )

    @patch("sync_service.cloud.yandex_disk.requests.put")
    @patch("sync_service.cloud.yandex_disk.requests.get")
    def test_load_uploads_file(self, mock_get, mock_put):
        disk = _make_disk(mock_get, mock_put)
        with tempfile.TemporaryDirectory() as tmp:
            local = os.path.join(tmp, "f.txt")
            with open(local, "w", encoding="utf-8") as fileobj:
                fileobj.write("hello")
            mock_get.return_value = _ok({"href": "https://upload.example/abc"})
            mock_put.return_value = _ok(status=201)
            disk.load(local)
        self.assertTrue(
            any(
                call.args and call.args[0] == "https://upload.example/abc"
                for call in mock_put.call_args_list
            )
        )

    @patch("sync_service.cloud.yandex_disk.requests.put")
    @patch("sync_service.cloud.yandex_disk.requests.get")
    def test_reload_uses_overwrite_true(self, mock_get, mock_put):
        disk = _make_disk(mock_get, mock_put)
        with tempfile.TemporaryDirectory() as tmp:
            local = os.path.join(tmp, "f.txt")
            with open(local, "w", encoding="utf-8") as fileobj:
                fileobj.write("hi")
            mock_get.return_value = _ok({"href": "https://upload.example/x"})
            mock_put.return_value = _ok(status=200)
            disk.reload(local)
        upload_request = mock_get.call_args_list[-1]
        self.assertEqual(upload_request.kwargs["params"]["overwrite"], "true")


if __name__ == "__main__":
    unittest.main()
