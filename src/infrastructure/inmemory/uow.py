"""In-memory unit of work."""

from __future__ import annotations

from src.domain.wallet.entity import BonusAccount, BonusLedgerEntry, LedgerOperation
from src.infrastructure.inmemory.repositories import (
    InMemoryBonusAccountRepository,
    InMemoryBonusLedgerRepository,
)


class InMemoryUnitOfWork:
    """No-op unit of work backed by process-local in-memory state."""

    def __init__(
        self,
        accounts: dict[str, BonusAccount],
        entries: list[BonusLedgerEntry],
        by_idempotency: dict[tuple[str, LedgerOperation, str], BonusLedgerEntry],
        by_reference: dict[tuple[str, LedgerOperation, str], BonusLedgerEntry],
    ) -> None:
        self.accounts = InMemoryBonusAccountRepository(accounts)
        self.ledger = InMemoryBonusLedgerRepository(
            entries=entries,
            by_idempotency=by_idempotency,
            by_reference=by_reference,
        )

    def __enter__(self) -> "InMemoryUnitOfWork":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def commit(self) -> None:
        return None
