"""HTTP error mapping helpers."""

from __future__ import annotations

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.domain.errors import (
    AccessDeniedError,
    DomainError,
    InvariantViolationError,
    NotFoundError,
    ValidationError,
)
from src.interface.http import problem_types


def _request_id(request: Request) -> str | None:
    return getattr(request.state, "request_id", None)


def _correlation_id(request: Request) -> str | None:
    return getattr(request.state, "correlation_id", None)


def _headers(request: Request, extra: dict[str, str] | None = None) -> dict[str, str]:
    headers = dict(extra or {})
    request_id = _request_id(request)
    correlation_id = _correlation_id(request)
    if request_id is not None:
        headers["X-Request-ID"] = request_id
    if correlation_id is not None:
        headers["X-Correlation-ID"] = correlation_id
    return headers


def _problem(
    request: Request,
    *,
    status: int,
    title: str,
    detail: object,
    problem_type: str,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={
            "type": problem_type,
            "title": title,
            "status": status,
            "detail": detail,
            "instance": str(request.url.path),
            "request_id": _request_id(request),
            "correlation_id": _correlation_id(request),
        },
        media_type="application/problem+json",
        headers=_headers(request, headers),
    )


async def domain_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Convert domain errors into `application/problem+json` responses."""

    mapping: dict[type[Exception], tuple[int, str, str]] = {
        ValidationError: (422, "Ошибка валидации", problem_types.VALIDATION),
        NotFoundError: (404, "Не найдено", problem_types.NOT_FOUND),
        AccessDeniedError: (403, "Доступ запрещен", problem_types.ACCESS_DENIED),
        InvariantViolationError: (409, "Нарушение инварианта", problem_types.CONFLICT),
    }
    status, title, problem_type = mapping.get(
        type(exc),
        (500, "Внутренняя ошибка", "about:blank"),
    )
    return _problem(
        request,
        status=status,
        title=title,
        detail=str(exc),
        problem_type=problem_type,
    )


async def unexpected_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Fallback problem response for unexpected exceptions."""

    return _problem(
        request,
        status=500,
        title="Внутренняя ошибка",
        detail="Unhandled server error.",
        problem_type=problem_types.INTERNAL_ERROR,
    )


async def validation_error_handler(
    request: Request,
    exc: RequestValidationError | PydanticValidationError,
) -> JSONResponse:
    """Convert request/model validation errors into `application/problem+json`."""

    return _problem(
        request,
        status=422,
        title="Ошибка валидации",
        detail=str(exc),
        problem_type=problem_types.VALIDATION,
    )


async def http_error_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    """Convert FastAPI/Starlette HTTP errors into `application/problem+json`."""

    mapping = {
        401: ("Не авторизован", problem_types.UNAUTHORIZED),
        403: ("Доступ запрещен", problem_types.ACCESS_DENIED),
        404: ("Не найдено", problem_types.NOT_FOUND),
        409: ("Конфликт", problem_types.CONFLICT),
        422: ("Ошибка валидации", problem_types.VALIDATION),
    }
    title, problem_type = mapping.get(exc.status_code, (str(exc.detail), "about:blank"))
    return _problem(
        request,
        status=exc.status_code,
        title=title,
        detail=exc.detail,
        problem_type=problem_type,
        headers=exc.headers,
    )


def register_exception_handlers(app) -> None:
    """Register shared exception handlers on the FastAPI app."""

    app.add_exception_handler(DomainError, domain_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(PydanticValidationError, validation_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_error_handler)
    app.add_exception_handler(Exception, unexpected_error_handler)
