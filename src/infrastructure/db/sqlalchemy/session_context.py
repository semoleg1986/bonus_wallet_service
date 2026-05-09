"""Current-session context for SQLAlchemy UoW."""

from __future__ import annotations

from contextvars import ContextVar

from sqlalchemy.orm import Session

_CURRENT_SESSION: ContextVar[Session | None] = ContextVar(
    "bonus_current_sqlalchemy_session",
    default=None,
)


def get_current_session() -> Session | None:
    """Return current UnitOfWork session."""

    return _CURRENT_SESSION.get()


def set_current_session(session: Session | None) -> object:
    """Set current UnitOfWork session and return reset token."""

    return _CURRENT_SESSION.set(session)


def reset_current_session(token: object) -> None:
    """Reset session context to previous state."""

    _CURRENT_SESSION.reset(token)  # type: ignore[arg-type]
