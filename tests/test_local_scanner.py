"""Тесты для ``local_scanner``."""

import os
import tempfile
import unittest

from sync_service.local_scanner import collect_local_files


class CollectLocalFilesTests(unittest.TestCase):
    """Сканирование папки."""

    def test_returns_only_files_with_mtime(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            file_path = os.path.join(tmp, "a.txt")
            with open(file_path, "w", encoding="utf-8") as fileobj:
                fileobj.write("hello")
            os.makedirs(os.path.join(tmp, "subdir"))
            result = collect_local_files(tmp)
            self.assertEqual(set(result), {"a.txt"})
            self.assertAlmostEqual(
                result["a.txt"], os.path.getmtime(file_path), places=3
            )

    def test_empty_folder(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(collect_local_files(tmp), {})


if __name__ == "__main__":
    unittest.main()
