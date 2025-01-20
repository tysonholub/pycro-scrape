import logging
import os
import sys

from redis.asyncio import Redis as AsyncRedis

from pycro_scrape.config import Settings


class ProdSettings(Settings):
    def __init__(self):
        logging.basicConfig(level=logging.INFO, stream=sys.stdout, force=True, format=self.LOGGING_FORMAT)

        # fast fail if environment settings are missing.
        self._base_url = os.environ["BASE_URL"]
        self._app_root = os.environ["APP_ROOT"]
        self._redis_endpoint = os.environ["REDIS_ENDPOINT"]
        self._redis_port = int(os.environ["REDIS_PORT"])

        # optional settings
        self._api_prefix = os.environ.get("API_PREFIX", "/api")
        self._api_title = os.environ.get("API_TITLE", "pycro-scrape")
        self._request_timeout = int(os.environ.get("REQUEST_TIMEOUT", 5))

        self._redis = None

    @property
    def testing(self) -> bool:
        return False

    @property
    def base_url(self) -> str:
        return self._base_url

    @property
    def environment(self) -> str:
        return "production"

    @property
    def api_prefix(self) -> str:
        return self._api_prefix

    @property
    def app_root(self) -> str:
        return self._app_root

    @property
    def redis_endpoint(self) -> str:
        return self._redis_endpoint

    @property
    def redis_port(self) -> int:
        return self._redis_port

    @property
    def request_timeout(self) -> int:
        return self._request_timeout

    @property
    def redis(self) -> AsyncRedis:
        if self._redis is None:
            self._redis = AsyncRedis(host=self.redis_endpoint, port=self.redis_port, decode_responses=False)

        return self._redis

    @property
    def fast_api_extras(self) -> dict:
        return {
            "openapi_url": f"{self.api_prefix}/openapi.json",
            "docs_url": f"{self.api_prefix}/docs",
            "redoc_url": f"{self.api_prefix}/redoc",
            "swagger_ui_oauth2_redirect_url": f"{self.api_prefix}/docs/oauth2-redirect",
            "title": self._api_title,
            "version": "v1",
        }


settings = ProdSettings()
