"""HTTP error mapping helpers."""

from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse

from src.domain.errors import (
    AccessDeniedError,
    DomainError,
    InvariantViolationError,
    NotFoundError,
    ValidationError,
)
from src.interface.http import problem_types


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
    request_id = getattr(request.state, "request_id", None)
    correlation_id = getattr(request.state, "correlation_id", None)
    return JSONResponse(
        status_code=status,
        content={
            "type": problem_type,
            "title": title,
            "status": status,
            "detail": str(exc),
            "instance": str(request.url.path),
            "request_id": request_id,
            "correlation_id": correlation_id,
        },
        media_type="application/problem+json",
    )


async def unexpected_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Fallback problem response for unexpected exceptions."""

    request_id = getattr(request.state, "request_id", None)
    correlation_id = getattr(request.state, "correlation_id", None)
    return JSONResponse(
        status_code=500,
        content={
            "type": "about:blank",
            "title": "Внутренняя ошибка",
            "status": 500,
            "detail": "Unhandled server error.",
            "instance": str(request.url.path),
            "request_id": request_id,
            "correlation_id": correlation_id,
        },
        media_type="application/problem+json",
    )


def register_exception_handlers(app) -> None:
    """Register shared exception handlers on the FastAPI app."""

    app.add_exception_handler(DomainError, domain_error_handler)
    app.add_exception_handler(Exception, unexpected_error_handler)
