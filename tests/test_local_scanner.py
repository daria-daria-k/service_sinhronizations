import os
import tempfile
import unittest
from sync_service.local_scanner import collect_local_files


class TestLocalScanner(unittest.TestCase):
    files = {
        'file1': 'test content',
        'file2': 'test content',
        'file3': 'test content',
    }

    dirs = ['dir1', 'dir2']

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.local_dir_with_files = os.path.join(self._tmp.name, 'files')
        self.local_dir_empty = os.path.join(self._tmp.name, 'empty')

        os.makedirs(self.local_dir_with_files)
        os.makedirs(self.local_dir_empty)

    def tearDown(self):
        self._tmp.cleanup()

    def _create_local_file(self, file_path):
        for file_name, content in self.files.items():
            with open(os.path.join(file_path, file_name), 'w') as f:
                f.write(content)

    def _create_local_dir(self, dir_path):
        for dir_name in self.dirs:
            os.makedirs(os.path.join(dir_path, dir_name))

    def test_valid_dict_with_files(self):
        """Проверяет что функция возвращает только файлы, игнорируя папки."""
        self._create_local_file(self.local_dir_with_files)
        self._create_local_dir(self.local_dir_with_files)
        self._create_local_file(os.path.join(self.local_dir_with_files, 'dir1'))

        local_files = collect_local_files(self.local_dir_with_files)

        self.assertEqual(len(local_files), 3)

    def test_valid_empty_dict(self):
        """Проверяет что функция возвращает пустой словарь, если в папке нет файлов, но присутствуют директории"""
        self._create_local_dir(self.local_dir_empty)

        local_files = collect_local_files(self.local_dir_empty)

        self.assertEqual(len(local_files), 0)
