"""The HTTP interface of the application."""

import os

from collections.abc import Awaitable, Callable
from typing import Annotated, cast

from fastapi import FastAPI, Path, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.responses import Response

from app.application.greet import greet

MAX_NAME_LENGTH = 100
PROBLEM_MEDIA_TYPE = "application/problem+json"
SECURITY_HEADERS = {
    "Cache-Control": "no-store",
    "Content-Security-Policy": "default-src 'none'; frame-ancestors 'none'",
    "Referrer-Policy": "no-referrer",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
}


class GreetingResponse(BaseModel):
    """The body of a successful greeting."""

    message: str


def create_app() -> FastAPI:
    """Build the HTTP application: one validated endpoint and no interactive documentation."""
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    app.add_exception_handler(RequestValidationError, _invalid_request)
    app.add_exception_handler(Exception, _server_error)

    @app.middleware("http")
    async def add_security_headers(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        return _with_security_headers(await call_next(request))

    @app.get("/greetings/{name}")
    async def greeting(
        name: Annotated[str, Path(max_length=MAX_NAME_LENGTH)],
    ) -> GreetingResponse:
        return GreetingResponse(message=greet(name))

    return app


def _invalid_request(_: Request, error: Exception) -> JSONResponse:
    fields: dict[str, list[str]] = {}
    for detail in cast(RequestValidationError, error).errors():
        fields.setdefault(str(detail["loc"][-1]), []).append(str(detail["msg"]))
    return _problem(400, "Invalid request", {"errors": fields})


def _problem(status: int, title: str, extra: dict[str, object] | None = None) -> JSONResponse:
    body: dict[str, object] = {"type": "about:blank", "title": title, "status": status}
    return JSONResponse(body | (extra or {}), status_code=status, media_type=PROBLEM_MEDIA_TYPE)


def _server_error(_: Request, __: Exception) -> JSONResponse:
    # The outermost middleware answers unhandled errors, so the headers are added here too.
    response = _problem(500, "An error occurred while processing your request.")
    return _with_security_headers(response)


def _with_security_headers[ResponseT: Response](response: ResponseT) -> ResponseT:
    response.headers.update(SECURITY_HEADERS)
    return response
