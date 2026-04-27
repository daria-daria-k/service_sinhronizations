"""Тесты для модуля ``config_loader``."""

import os
import tempfile
import unittest

from sync_service.config_loader import ConfigError, load_config


_VALID_TEMPLATE = """[sync]
local_path = {local_path}
remote_name = backup
token = AQAAAAA-test-token
period = 30
log_path = {log_path}
"""


class LoadConfigTests(unittest.TestCase):
    """Сценарии разбора ``config.ini``."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.local_dir = os.path.join(self._tmp.name, "data")
        os.makedirs(self.local_dir)
        self.log_path = os.path.join(self._tmp.name, "sync.log")
        self.config_path = os.path.join(self._tmp.name, "config.ini")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _write_config(self, body: str) -> None:
        with open(self.config_path, "w", encoding="utf-8") as fileobj:
            fileobj.write(body)

    def test_loads_valid_config(self) -> None:
        self._write_config(
            _VALID_TEMPLATE.format(
                local_path=self.local_dir, log_path=self.log_path
            )
        )
        config = load_config(self.config_path)
        self.assertEqual(config.local_path, self.local_dir)
        self.assertEqual(config.remote_name, "backup")
        self.assertEqual(config.token, "AQAAAAA-test-token")
        self.assertEqual(config.period, 30)
        self.assertEqual(config.log_path, self.log_path)

    def test_missing_file_raises(self) -> None:
        with self.assertRaises(ConfigError):
            load_config(os.path.join(self._tmp.name, "nope.ini"))

    def test_missing_section_raises(self) -> None:
        self._write_config("[other]\nkey=value\n")
        with self.assertRaises(ConfigError):
            load_config(self.config_path)

    def test_missing_local_folder_raises(self) -> None:
        self._write_config(
            _VALID_TEMPLATE.format(
                local_path=os.path.join(self._tmp.name, "ghost"),
                log_path=self.log_path,
            )
        )
        with self.assertRaises(ConfigError):
            load_config(self.config_path)

    def test_invalid_period_raises(self) -> None:
        body = _VALID_TEMPLATE.format(
            local_path=self.local_dir, log_path=self.log_path
        ).replace("period = 30", "period = abc")
        self._write_config(body)
        with self.assertRaises(ConfigError):
            load_config(self.config_path)

    def test_empty_token_raises(self) -> None:
        body = _VALID_TEMPLATE.format(
            local_path=self.local_dir, log_path=self.log_path
        ).replace("token = AQAAAAA-test-token", "token =   ")
        self._write_config(body)
        with self.assertRaises(ConfigError):
            load_config(self.config_path)


if __name__ == "__main__":
    unittest.main()
