"""FastAPI application factory."""

from fastapi import FastAPI

from src.domain.errors import DomainError
from src.interface.http.errors import domain_error_handler, register_exception_handlers
from src.interface.http.health import router as health_router
from src.interface.http.observability import (
    configure_http_logging,
    install_observability,
)
from src.interface.http.v1.admin.router import router as admin_bonus_router
from src.interface.http.v1.internal.router import router as internal_bonus_router
from src.interface.http.v1.parent.router import router as parent_bonus_router


def create_app() -> FastAPI:
    """Create and configure HTTP application."""

    configure_http_logging()
    app = FastAPI(title="bonus_wallet_service")
    install_observability(app)
    app.include_router(health_router)
    app.include_router(internal_bonus_router)
    app.include_router(parent_bonus_router)
    app.include_router(admin_bonus_router)
    app.add_exception_handler(DomainError, domain_error_handler)
    register_exception_handlers(app)
    return app
