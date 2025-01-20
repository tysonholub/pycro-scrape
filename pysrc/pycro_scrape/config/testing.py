import os

from fakeredis.aioredis import FakeRedis as AsyncFakeRedis

from pycro_scrape.config import Settings


class TestSettings(Settings):
    def __init__(self):
        self._redis = AsyncFakeRedis(host=self.redis_endpoint, port=self.redis_port, decode_responses=False)
        self._api_prefix = "/api"
        self._api_title = "pycro-scrape"

    @property
    def testing(self) -> bool:
        return True

    @property
    def base_url(self) -> str:
        return "http://127.0.0.1:5001"

    @property
    def environment(self) -> str:
        return "testing"

    @property
    def api_prefix(self) -> str:
        return self._api_prefix

    @property
    def app_root(self) -> str:
        return os.getcwd()

    @property
    def redis_endpoint(self) -> str:
        return "redis-endpoint"

    @property
    def redis_port(self) -> int:
        return 6379

    @property
    def request_timeout(self) -> int:
        return 5

    @property
    def redis(self) -> AsyncFakeRedis:
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


settings = TestSettings()
