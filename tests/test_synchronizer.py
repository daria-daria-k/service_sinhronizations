import unittest
from sync_service.synchronizer import diff


class TestSynchronizer(unittest.TestCase):
    def test_file_uploaded_when_not_in_cloud(self):
        """Проверяет корректность списка для добавления файлов в облако, которые есть локально"""
        current_local = {
            'file1.txt': 1000.0,
        }
        previous_local = {
        }
        remote_files = {
        }

        to_upload, _, _ = diff(current_local, previous_local, remote_files)

        self.assertEqual(to_upload, {'file1.txt'})

    def test_file_deleted_when_not_local(self):
        """Проверяет корректность списка для удаления файлов из облака, которых нет локально"""
        current_local = {
        }
        previous_local = {
        }
        remote_files = {
            'file2.txt': 1000.0
        }

        _, to_delete, _ = diff(current_local, previous_local, remote_files)

        self.assertEqual(to_delete, {'file2.txt'})

    def test_file_reloaded_when_mtime_changed(self):
        """Проверяет корректность списка для обновления файлов в облаке"""
        current_local = {
            'file2.txt': 2000.0
        }
        previous_local = {
            'file2.txt': 1000.0
        }
        remote_files = {
            'file2.txt': 1000.0
        }

        _, _, to_reload = diff(current_local, previous_local, remote_files)

        self.assertEqual(to_reload, {'file2.txt'})
