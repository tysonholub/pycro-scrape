from fastapi import FastAPI, Response

from pycro_scrape.api import v1
from pycro_scrape.api.exceptions import APIError
from pycro_scrape.config import settings


def create_app() -> FastAPI:
    app = FastAPI(**settings.fast_api_extras)
    app.get("/health", include_in_schema=False)(lambda: Response(status_code=200))
    app.include_router(v1.router)
    APIError.init_app(app)

    return app
