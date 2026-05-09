"""HTTP observability helpers for bonus_wallet_service."""

from __future__ import annotations

import json
import logging
import os
import time
from collections import defaultdict
from datetime import datetime, timezone
from threading import Lock
from uuid import uuid4

from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import PlainTextResponse, Response

_LOGGER = logging.getLogger("bonus_wallet_service.http")
_SERVICE = "bonus_wallet_service"
_METRICS_LOCK = Lock()
_REQUESTS_TOTAL: dict[tuple[str, str, str, str], int] = defaultdict(int)
_REQUEST_DURATION_SUM: dict[tuple[str, str, str], float] = defaultdict(float)
_REQUEST_DURATION_COUNT: dict[tuple[str, str, str], int] = defaultdict(int)
_ERRORS_TOTAL: dict[tuple[str, str, str], int] = defaultdict(int)


def _apply_security_headers(response: Response) -> None:
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"


def _metrics_access_allowed(request: Request) -> bool:
    expected_token = os.getenv("BONUS_METRICS_TOKEN")
    if not expected_token:
        return True

    service_token = request.headers.get("X-Service-Token")
    if service_token == expected_token:
        return True

    authorization = request.headers.get("Authorization", "")
    return authorization == f"Bearer {expected_token}"


def configure_http_logging() -> None:
    """Enable compact JSON logging for HTTP events."""

    logging.basicConfig(level=logging.INFO, format="%(message)s")


def reset_metrics() -> None:
    """Reset accumulated metrics, mainly for tests."""

    with _METRICS_LOCK:
        _REQUESTS_TOTAL.clear()
        _REQUEST_DURATION_SUM.clear()
        _REQUEST_DURATION_COUNT.clear()
        _ERRORS_TOTAL.clear()


class _StructuredHttpLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        request_id = request.headers.get("X-Request-ID") or uuid4().hex
        correlation_id = request.headers.get("X-Correlation-ID") or request_id
        request.state.request_id = request_id
        request.state.correlation_id = correlation_id
        started_at = time.perf_counter()
        status_code = 500
        path = request.url.path

        try:
            response = await call_next(request)
            status_code = response.status_code
            route = request.scope.get("route")
            path = getattr(route, "path", request.url.path)
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Correlation-ID"] = correlation_id
            _apply_security_headers(response)
            return response
        finally:
            duration_seconds = time.perf_counter() - started_at
            duration_ms = round(duration_seconds * 1000, 2)
            status = str(status_code)

            with _METRICS_LOCK:
                _REQUESTS_TOTAL[(_SERVICE, request.method, path, status)] += 1
                _REQUEST_DURATION_SUM[
                    (_SERVICE, request.method, path)
                ] += duration_seconds
                duration_key = (_SERVICE, request.method, path)
                _REQUEST_DURATION_COUNT[duration_key] += 1
                if status_code >= 400:
                    _ERRORS_TOTAL[(_SERVICE, path, status)] += 1

            event = {
                "ts": datetime.now(timezone.utc).isoformat(),
                "service": _SERVICE,
                "event": "http_request",
                "request_id": request_id,
                "correlation_id": correlation_id,
                "method": request.method,
                "path": path,
                "query": request.url.query,
                "status_code": status_code,
                "duration_ms": duration_ms,
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
            }
            _LOGGER.info(json.dumps(event, ensure_ascii=False))


def install_observability(app: FastAPI) -> None:
    """Install request ids, metrics, headers, and structured logging."""

    @app.get("/metrics", include_in_schema=False)
    async def metrics(request: Request) -> PlainTextResponse:
        if not _metrics_access_allowed(request):
            return PlainTextResponse("Unauthorized\n", status_code=401)

        lines = [
            "# HELP http_requests_total Total HTTP requests.",
            "# TYPE http_requests_total counter",
        ]
        with _METRICS_LOCK:
            for (service, method, path, status), value in sorted(
                _REQUESTS_TOTAL.items()
            ):
                labels = (
                    f'service="{service}",method="{method}",'
                    f'path="{path}",status="{status}"'
                )
                lines.append(f"http_requests_total{{{labels}}} {value}")
            lines.extend(
                [
                    (
                        "# HELP http_request_duration_seconds HTTP request latency "
                        "in seconds."
                    ),
                    "# TYPE http_request_duration_seconds summary",
                ]
            )
            for (service, method, path), duration_sum in sorted(
                _REQUEST_DURATION_SUM.items()
            ):
                count = _REQUEST_DURATION_COUNT[(service, method, path)]
                labels = f'service="{service}",method="{method}",path="{path}"'
                lines.append(
                    f"http_request_duration_seconds_sum{{{labels}}} {duration_sum}"
                )
                lines.append(f"http_request_duration_seconds_count{{{labels}}} {count}")
            lines.extend(
                [
                    (
                        "# HELP http_errors_total Total HTTP error responses "
                        "(status >= 400)."
                    ),
                    "# TYPE http_errors_total counter",
                ]
            )
            for (service, path, status), value in sorted(_ERRORS_TOTAL.items()):
                labels = f'service="{service}",path="{path}",status="{status}"'
                lines.append(f"http_errors_total{{{labels}}} {value}")

        return PlainTextResponse(
            content="\n".join(lines) + "\n",
            media_type="text/plain; version=0.0.4; charset=utf-8",
        )

    app.add_middleware(_StructuredHttpLogMiddleware)
