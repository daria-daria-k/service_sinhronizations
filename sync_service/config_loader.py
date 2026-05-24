import configparser
import os


class ConfigError(Exception):
    """Класс для идентификации ошибок, связанных с обработкой файла Config"""
    pass


class Config:
    """Класс для определения параметров конфига"""

    def __init__(self, local_path: str, remote_name: str, token: str, period: int, log_path: str) -> None:
        self.local_path = local_path
        self.remote_name = remote_name
        self.token = token
        self.period = period
        self.log_path = log_path


def load_config(path: str) -> Config:
    """Читает config.ini и возвращает объект Config.

    :param path: путь к файлу конфигурации
    :raises ConfigError: если файл не найден, секция отсутствует или данные некорректны
    :return: объект Config с параметрами запуска
    """

    parser = configparser.ConfigParser()
    if os.path.isfile(path):
        try:
            parser.read(path, encoding='utf-8')
        except configparser.MissingSectionHeaderError:
            raise ConfigError('Файл конфигурации имеет неверный формат')
    else:
        raise ConfigError(f'Файла {path} не существует')

    if not parser.has_section('sync'):
        raise ConfigError('В config.ini нет секции [sync]')
    section = parser['sync']

    required_keys = ['local_path', 'remote_name', 'token', 'period', 'log_path']
    missing = [key for key in required_keys if key not in section]
    if missing:
        raise ConfigError(f'Не хватает параметров: {", ".join(missing)}')

    if not section['token'].strip():
        raise ConfigError('Переменная token не может быть пустой')

    try:
        if int(section['period']) <= 0:
            raise ConfigError('Переменная period должна быть положительным числом больше 0')
    except ValueError:
        raise ConfigError(f'period должен быть числом, получено: {section["period"]}')

    if not os.path.isdir(section['local_path']):
        raise ConfigError(f'Директория {section["local_path"]} не существует')

    return Config(
        local_path=section['local_path'],
        remote_name=section['remote_name'],
        token=section['token'],
        period=int(section['period']),
        log_path=section['log_path']
    )
