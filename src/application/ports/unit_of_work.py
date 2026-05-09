"""Unit-of-work contract."""

from __future__ import annotations

from typing import Callable, Protocol, Self

from src.application.ports.repositories import (
    BonusAccountRepositoryPort,
    BonusLedgerRepositoryPort,
)


class UnitOfWork(Protocol):
    """Boundary for write-side transactions."""

    accounts: BonusAccountRepositoryPort
    ledger: BonusLedgerRepositoryPort

    def __enter__(self) -> Self:
        """Enter transactional scope."""

    def __exit__(self, exc_type, exc, tb) -> None:
        """Exit transactional scope."""

    def commit(self) -> None:
        """Commit pending changes."""


UnitOfWorkFactory = Callable[[], UnitOfWork]
