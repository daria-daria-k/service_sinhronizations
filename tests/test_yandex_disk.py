import unittest
from unittest.mock import patch, MagicMock
from sync_service.cloud.yandex_disk import YandexDisk
from sync_service.cloud.base import CloudAuthError, CloudStorageError


class TestYandexDisk(unittest.TestCase):
    @patch('sync_service.cloud.yandex_disk.requests.get')
    def test_invalid_token_raises(self, mock_get):
        """Проверяет что неверный токен вызывает CloudAuthError."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        with self.assertRaises(CloudAuthError):
            YandexDisk('bad_token', 'backup')


    @patch('sync_service.cloud.yandex_disk.requests.put')
    @patch('sync_service.cloud.yandex_disk.requests.get')
    def test_get_info_returns_dict(self, mock_get, mock_put):
        """Проверяет что get_info возвращает словарь имя: время."""
        mock_get.return_value = MagicMock(status_code=200, json=lambda: {
            '_embedded': {
                'items': [
                    {'name': 'file1.txt', 'modified': '2026-01-01'},
                    {'name': 'file2.txt', 'modified': '2026-01-02'},
                ]
            }
        })
        mock_put.return_value = MagicMock(status_code=201)

        disk = YandexDisk('token', 'backup')
        info = disk.get_info()

        self.assertEqual(info, {'file1.txt': '2026-01-01', 'file2.txt': '2026-01-02'})


    @patch('sync_service.cloud.yandex_disk.requests.delete')
    @patch('sync_service.cloud.yandex_disk.requests.put')
    @patch('sync_service.cloud.yandex_disk.requests.get')
    def test_delete_raises_on_failure(self, mock_get, mock_put, mock_delete):
        """Проверяет что delete бросает CloudStorageError при ошибке."""
        mock_get.return_value = MagicMock(status_code=200, json=lambda: {})
        mock_put.return_value = MagicMock(status_code=201)
        mock_delete.return_value = MagicMock(status_code=500, text='error')

        disk = YandexDisk('token', 'backup')

        with self.assertRaises(CloudStorageError):
            disk.delete('file1.txt')
