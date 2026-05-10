"""HTTP dependency wiring."""

from __future__ import annotations

from functools import lru_cache

from src.application.ports.access_token_verifier import AccessTokenVerifier
from src.application.services.facade import BonusWalletFacade
from src.domain.wallet.entity import BonusAccount, BonusLedgerEntry, LedgerOperation
from src.domain.wallet.rule import BonusRule
from src.infrastructure.auth.jwks_access_token_verifier import JwksAccessTokenVerifier
from src.infrastructure.config.settings import Settings
from src.infrastructure.db.sqlalchemy.base import Base
from src.infrastructure.db.sqlalchemy.session import build_engine, build_session_factory
from src.infrastructure.db.sqlalchemy.uow import SqlAlchemyUnitOfWork
from src.infrastructure.inmemory.uow import InMemoryUnitOfWork

_ACCOUNTS: dict[str, BonusAccount] = {}
_ENTRIES: list[BonusLedgerEntry] = []
_ENTRIES_BY_IDEMPOTENCY: dict[tuple[str, LedgerOperation, str], BonusLedgerEntry] = {}
_ENTRIES_BY_REFERENCE: dict[tuple[str, LedgerOperation, str], BonusLedgerEntry] = {}
_RULES: dict[str, BonusRule] = {}


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return singleton runtime settings."""

    return Settings.from_env()


@lru_cache(maxsize=1)
def get_engine():
    """Return shared SQLAlchemy engine for SQL-backed runtime."""

    settings = get_settings()
    engine = build_engine(settings.database_url)
    if settings.auto_create_schema:
        Base.metadata.create_all(engine)
    return engine


@lru_cache(maxsize=1)
def get_session_factory():
    """Return shared SQLAlchemy session factory."""

    return build_session_factory(get_engine())


def get_facade() -> BonusWalletFacade:
    """Return runtime application facade."""

    settings = get_settings()
    if not settings.use_inmemory:
        return BonusWalletFacade(
            uow_factory=lambda: SqlAlchemyUnitOfWork(get_session_factory())
        )

    return BonusWalletFacade(
        uow_factory=lambda: InMemoryUnitOfWork(
            accounts=_ACCOUNTS,
            entries=_ENTRIES,
            by_idempotency=_ENTRIES_BY_IDEMPOTENCY,
            by_reference=_ENTRIES_BY_REFERENCE,
            rules=_RULES,
        )
    )


@lru_cache(maxsize=1)
def get_access_token_verifier() -> AccessTokenVerifier:
    """Return singleton access token verifier."""

    settings = get_settings()
    return JwksAccessTokenVerifier(
        issuer=settings.auth_issuer,
        audience=settings.auth_audience,
        jwks_url=settings.auth_jwks_url,
        jwks_json=settings.auth_jwks_json,
    )


def reset_runtime_state() -> None:
    """Reset process-local runtime state for tests."""

    _ACCOUNTS.clear()
    _ENTRIES.clear()
    _ENTRIES_BY_IDEMPOTENCY.clear()
    _ENTRIES_BY_REFERENCE.clear()
    _RULES.clear()
    get_settings.cache_clear()
    get_engine.cache_clear()
    get_session_factory.cache_clear()
    get_access_token_verifier.cache_clear()
