"""Чтение и валидация ``config.ini``."""

import configparser
import os
from typing import NamedTuple


class ConfigError(Exception):
    """Ошибка в файле конфигурации."""


class Config(NamedTuple):
    """Параметры запуска сервиса."""

    local_path: str
    remote_name: str
    token: str
    period: int
    log_path: str


_REQUIRED_KEYS = ("local_path", "remote_name", "token", "period", "log_path")


def load_config(config_path: str) -> Config:
    """Прочитать ``config.ini`` и вернуть валидный ``Config``.

    :raises ConfigError: при отсутствии файла, секции, ключа или папки,
        либо при некорректном значении ``period``/``token``.
    """
    parser = _read_parser(config_path)
    raw = _extract_section(parser)
    _ensure_required_keys(raw)
    period = _parse_period(raw["period"])
    _ensure_token(raw["token"])
    _ensure_local_folder(raw["local_path"])
    return Config(
        local_path=raw["local_path"],
        remote_name=raw["remote_name"],
        token=raw["token"],
        period=period,
        log_path=raw["log_path"],
    )


def _read_parser(config_path: str) -> configparser.ConfigParser:
    """Создать ``ConfigParser`` и прочитать файл."""
    if not os.path.isfile(config_path):
        raise ConfigError(f"Файл конфигурации не найден: {config_path}")
    parser = configparser.ConfigParser()
    parser.read(config_path, encoding="utf-8")
    return parser


def _extract_section(parser: configparser.ConfigParser) -> dict:
    """Достать секцию ``[sync]`` как обычный словарь."""
    if not parser.has_section("sync"):
        raise ConfigError("В config.ini отсутствует секция [sync].")
    return dict(parser.items("sync"))


def _ensure_required_keys(raw: dict) -> None:
    """Проверить, что в секции есть все нужные ключи."""
    missing = [key for key in _REQUIRED_KEYS if key not in raw]
    if missing:
        raise ConfigError(
            f"В секции [sync] не хватает параметров: {', '.join(missing)}"
        )


def _parse_period(value: str) -> int:
    """Превратить ``period`` в положительное целое число."""
    try:
        period = int(value)
    except ValueError as exc:
        raise ConfigError(
            f"Параметр period должен быть целым числом, получено: '{value}'"
        ) from exc
    if period <= 0:
        raise ConfigError("Параметр period должен быть положительным.")
    return period


def _ensure_token(token: str) -> None:
    """Убедиться, что токен не пустой."""
    if not token.strip():
        raise ConfigError("Параметр token не должен быть пустым.")


def _ensure_local_folder(local_path: str) -> None:
    """Убедиться, что синхронизируемая папка существует."""
    if not os.path.isdir(local_path):
        raise ConfigError(
            f"Синхронизируемая папка не найдена: {local_path}"
        )
