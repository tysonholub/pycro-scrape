from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


class FetchArgs(BaseModel):
    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"]
    url: str
    headers: dict[str, str] = Field(default_factory=dict)
    post_data: dict[str, Any] | None = None

    @model_validator(mode="before")
    @classmethod
    def validate(cls, values):
        result = {} | values

        result["method"] = values["method"].upper()

        return result


class PostSessionArgs(BaseModel):
    url: str
    browser: Literal["chrome", "firefox"]


class BrowserSession(BaseModel):
    id: str
    iat: int
    expires: int
    url: str
    cookies: list[dict[str, Any]] = Field(default_factory=list)
    local_storage: list[dict[str, Any]] = Field(default_factory=list)


class PostSessionResponse(BaseModel):
    session: BrowserSession
    html_response: str


class PostFetchSessionArgs(BaseModel):
    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"]
    url: str
    headers: dict[str, str] = Field(default_factory=dict)
    post_data: dict[str, Any] | None = None

    @model_validator(mode="before")
    @classmethod
    def validate(cls, values):
        result = {} | values

        result["method"] = values["method"].upper()

        return result


class PostFetchSessionResponse(BaseModel):
    session: BrowserSession
    fetch_response: str
