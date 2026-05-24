import sys
from sync_service.config_loader import load_config, ConfigError
from sync_service.logger import setup_logger
from sync_service.cloud.yandex_disk import YandexDisk
from sync_service.cloud.base import CloudAuthError, CloudStorageError
from sync_service.synchronizer import run_forever

# Читаем конфиг
try:
    config = load_config("config.ini")
except ConfigError as e:
    print(f"Ошибка конфигурации {e}")
    sys.exit(1)

# Настраиваем логи
logger = setup_logger(config.log_path)

# Задаем удаленное облако
try:
    yandex_disk = YandexDisk(config.token, config.remote_name)
except CloudAuthError as e:
    print(f"Ошибка аутентификации токена {e}")
    sys.exit(1)
except CloudStorageError as e:
    print(f"Ошибка в работе хранилища {e}")
    sys.exit(1)

# Запускаем бесконечный цикл
try:
    run_forever(yandex_disk, config.local_path, config.period, logger)
except KeyboardInterrupt:
    logger.info("Программа остановлена пользователем.")
