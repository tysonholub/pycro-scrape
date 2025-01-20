import os
import warnings
from abc import ABCMeta, abstractmethod
from importlib import import_module

from redis.asyncio import Redis as AsyncRedis


class Settings(metaclass=ABCMeta):
    LOGGING_FORMAT = "%(levelname)s:%(name)s:%(pathname)s:%(lineno)d:%(message)s"

    @property
    @abstractmethod
    def testing(self) -> bool:
        raise NotImplementedError()

    @property
    @abstractmethod
    def base_url(self) -> str:
        raise NotImplementedError()

    @property
    @abstractmethod
    def environment(self) -> str:
        raise NotImplementedError()

    @property
    @abstractmethod
    def api_prefix(self) -> str:
        raise NotImplementedError()

    @property
    @abstractmethod
    def app_root(self) -> str:
        raise NotImplementedError()

    @property
    @abstractmethod
    def redis_endpoint(self) -> str:
        raise NotImplementedError()

    @property
    @abstractmethod
    def redis_port(self) -> int:
        raise NotImplementedError()

    @property
    @abstractmethod
    def request_timeout(self) -> int:
        raise NotImplementedError()

    @property
    @abstractmethod
    def redis(self) -> AsyncRedis:
        raise NotImplementedError()

    @property
    @abstractmethod
    def fast_api_extras(self) -> dict:
        raise NotImplementedError


DEFAULT_SETTINGS_MODULE = "pycro_scrape.config.testing:settings"

_settings_module = os.getenv("PYCRO_SCRAPE_SETTINGS_MODULE", None)
if _settings_module is None:
    warnings.warn(f"PYCRO_SCRAPE_SETTINGS_MODULE not set, using default {DEFAULT_SETTINGS_MODULE!r}", stacklevel=1)
    _settings_module = DEFAULT_SETTINGS_MODULE

module, instance = _settings_module.split(":")
settings: Settings = getattr(import_module(module), instance)
