import logging
from logging.handlers import RotatingFileHandler


def setup_logger(log_path: str) -> logging.Logger:
    """
    Вывод информации о ходе работы программы в файл и консоль
    :param log_path:
    :return:
    """

    logger = logging.getLogger("sync_service")
    logger.setLevel(logging.INFO)

    file_handler = RotatingFileHandler(filename=log_path, encoding='utf-8', maxBytes=5 * 1024 * 1024, backupCount=3)
    stream_handler = logging.StreamHandler()

    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger
