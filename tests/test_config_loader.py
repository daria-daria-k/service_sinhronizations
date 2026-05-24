import os
import tempfile
import unittest
from sync_service.config_loader import load_config, ConfigError


class TestLoadConfig(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.local_dir = os.path.join(self._tmp.name, 'data')
        os.makedirs(self.local_dir)
        self.config_path = os.path.join(self._tmp.name, 'config.ini')

    def tearDown(self):
        self._tmp.cleanup()

    def _write_config(self, content):
        with open(self.config_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def test_valid_config(self):
        """Проверяет валидность конфига"""
        self._write_config(f"""[sync]
        local_path = {self.local_dir}
        remote_name = backup
        token = mytoken123
        period = 30
        log_path = sync.log
        """)

        config = load_config(self.config_path)
        self.assertEqual(config.log_path, "sync.log")
        self.assertEqual(config.token, 'mytoken123')
        self.assertEqual(config.period, 30)

    def test_missing_file_rises(self):
        """Проверка работу исключения в случае неверного пути к конфигу"""
        with self.assertRaises(ConfigError):
            load_config("/несуществующий/путь/config.ini")

    def test_missing_section_raises(self):
        """Проверяет работу исключения в случае если функция сборки информации о конфиге завершилась ошибкой"""
        self._write_config("local_path = /tmp\n")
        with self.assertRaises(ConfigError):
            load_config(self.config_path)

    def test_empty_token_raises(self):
        """Проверяет работу исключения в случае отсутствия значения токена"""
        self._write_config(f"""[sync]
        local_path = {self.local_dir}
        remote_name = backup
        token =
        period = 30
        log_path = sync.log
        """)
        with self.assertRaises(ConfigError):
            load_config(self.config_path)

    def test_invalid_period_raises(self):
        """Проверяет работу исключения в случае неправильного значения периода работы скрипта"""
        self._write_config(f"""[sync]
        local_path = {self.local_dir}
        remote_name = backup
        token = mytoken
        period = abc
        log_path = sync.log
        """)
        with self.assertRaises(ConfigError):
            load_config(self.config_path)

