"""SQLAlchemy UnitOfWork implementation."""

from __future__ import annotations

from sqlalchemy.orm import Session, sessionmaker

from src.infrastructure.db.sqlalchemy.account_repository_sqlalchemy import (
    SqlAlchemyBonusAccountRepository,
)
from src.infrastructure.db.sqlalchemy.ledger_repository_sqlalchemy import (
    SqlAlchemyBonusLedgerRepository,
)
from src.infrastructure.db.sqlalchemy.session_context import (
    reset_current_session,
    set_current_session,
)


class SqlAlchemyUnitOfWork:
    """Transactional UnitOfWork backed by a single SQLAlchemy session."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory
        self._session: Session | None = None
        self._token: object | None = None
        self.accounts: SqlAlchemyBonusAccountRepository
        self.ledger: SqlAlchemyBonusLedgerRepository

    def __enter__(self) -> "SqlAlchemyUnitOfWork":
        self._session = self._session_factory()
        self._token = set_current_session(self._session)
        self.accounts = SqlAlchemyBonusAccountRepository(self._session)
        self.ledger = SqlAlchemyBonusLedgerRepository(self._session)
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        try:
            if self._session is not None and exc is not None:
                self._session.rollback()
        finally:
            if self._token is not None:
                reset_current_session(self._token)
            if self._session is not None:
                self._session.close()
            self._session = None
            self._token = None

    def commit(self) -> None:
        """Commit transaction."""

        if self._session is None:
            return
        self._session.commit()
