from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


async def _exc_handler(request, exc):
    return exc.make_json_response()


class APIError(Exception):
    """Exception raised to short-circuit an API Request"""

    @classmethod
    def init_app(cls, app: FastAPI):
        app.add_exception_handler(cls, _exc_handler)

    def __init__(self, msg: str, code: int, error_fields: dict | None = None):
        self.msg = msg
        self.error_fields = error_fields or {}
        self.code = code
        super().__init__(msg)

    def make_json_response(self):
        content: dict = {"msg": self.msg}
        if self.error_fields:
            content.update({"error_fields": self.error_fields})

        return JSONResponse(status_code=self.code, content=jsonable_encoder({"detail": [content]}))
