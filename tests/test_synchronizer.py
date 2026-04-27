"""Тесты для ``synchronizer``."""

import logging
import unittest
from unittest.mock import MagicMock

from sync_service.cloud.base import CloudStorageError
from sync_service.synchronizer import apply_changes, diff, run_once


class DiffTests(unittest.TestCase):
    """Логика сравнения локальной и удалённой папок."""

    def test_first_run_only_uploads_and_deletes(self) -> None:
        current = {"a.txt": 100.0, "b.txt": 200.0}
        previous: dict = {}
        remote = {"b.txt", "c.txt"}
        upload, reload_, delete = diff(current, previous, remote)
        self.assertEqual(upload, {"a.txt"})
        self.assertEqual(reload_, set())
        self.assertEqual(delete, {"c.txt"})

    def test_reload_when_mtime_changed(self) -> None:
        current = {"a.txt": 200.0}
        previous = {"a.txt": 100.0}
        remote = {"a.txt"}
        _, reload_, _ = diff(current, previous, remote)
        self.assertEqual(reload_, {"a.txt"})

    def test_no_reload_when_unchanged(self) -> None:
        current = {"a.txt": 100.0}
        previous = {"a.txt": 100.0}
        remote = {"a.txt"}
        _, reload_, _ = diff(current, previous, remote)
        self.assertEqual(reload_, set())


class ApplyChangesTests(unittest.TestCase):
    """``apply_changes`` вызывает методы хранилища и логирует ошибки."""

    def setUp(self) -> None:
        self.storage = MagicMock()
        self.logger = MagicMock(spec=logging.Logger)

    def test_calls_load_reload_delete(self) -> None:
        apply_changes(
            self.storage, "/tmp", {"a"}, {"b"}, {"c"}, self.logger
        )
        self.storage.load.assert_called_once()
        self.storage.reload.assert_called_once()
        self.storage.delete.assert_called_once_with("c")

    def test_logs_error_and_continues_on_failure(self) -> None:
        self.storage.load.side_effect = CloudStorageError("boom")
        apply_changes(
            self.storage, "/tmp", {"a"}, set(), {"c"}, self.logger
        )
        self.logger.error.assert_called()
        self.storage.delete.assert_called_once_with("c")


class RunOnceTests(unittest.TestCase):
    """Поведение одного цикла синхронизации."""

    def test_returns_previous_state_on_get_info_failure(self) -> None:
        storage = MagicMock()
        storage.get_info.side_effect = CloudStorageError("network down")
        logger = MagicMock(spec=logging.Logger)
        previous = {"a.txt": 1.0}
        result = run_once(storage, "/nonexistent", previous, logger)
        self.assertEqual(result, previous)
        logger.error.assert_called()


if __name__ == "__main__":
    unittest.main()
