"""Infrastructure configuration for bonus_wallet_service."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Settings:
    """Runtime settings."""

    app_name: str
    app_host: str
    app_port: int
    database_url: str
    use_inmemory: bool
    auto_create_schema: bool
    auth_issuer: str
    auth_audience: str
    auth_jwks_url: str
    auth_jwks_json: str | None
    service_token: str

    @classmethod
    def from_env(cls) -> "Settings":
        """Build settings from environment variables."""

        return cls(
            app_name=os.getenv("BONUS_APP_NAME", "bonus_wallet_service"),
            app_host=os.getenv("BONUS_APP_HOST", "0.0.0.0"),
            app_port=int(os.getenv("BONUS_APP_PORT", "8006")),
            database_url=os.getenv(
                "BONUS_DATABASE_URL", "sqlite:///./bonus_wallet_service.db"
            ),
            use_inmemory=os.getenv("BONUS_USE_INMEMORY", "1") == "1",
            auto_create_schema=os.getenv("BONUS_AUTO_CREATE_SCHEMA", "0") == "1",
            auth_issuer=os.getenv("BONUS_AUTH_ISSUER", "auth_service"),
            auth_audience=os.getenv("BONUS_AUTH_AUDIENCE", "platform_clients"),
            auth_jwks_url=os.getenv(
                "BONUS_AUTH_JWKS_URL",
                "http://localhost:8000/.well-known/jwks.json",
            ),
            auth_jwks_json=os.getenv("BONUS_AUTH_JWKS_JSON"),
            service_token=os.getenv("BONUS_SERVICE_TOKEN", "dev-service-token"),
        )
