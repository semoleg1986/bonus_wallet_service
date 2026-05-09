"""Repository ports for wallet persistence."""

from __future__ import annotations

from typing import Protocol

from src.domain.wallet.entity import BonusAccount, BonusLedgerEntry, LedgerOperation


class BonusAccountRepositoryPort(Protocol):
    """Storage access for bonus accounts."""

    def get(self, parent_id: str) -> BonusAccount | None:
        """Return wallet account if present."""

    def save(self, account: BonusAccount) -> None:
        """Persist wallet account."""


class BonusLedgerRepositoryPort(Protocol):
    """Storage access for ledger entries."""

    def append(self, entry: BonusLedgerEntry) -> None:
        """Append a new ledger entry."""

    def get_by_idempotency(
        self,
        *,
        parent_id: str,
        operation: LedgerOperation,
        idempotency_key: str,
    ) -> BonusLedgerEntry | None:
        """Return entry by idempotency key for replay-safe writes."""

    def get_by_reference(
        self,
        *,
        parent_id: str,
        operation: LedgerOperation,
        reference_id: str,
    ) -> BonusLedgerEntry | None:
        """Return entry by external business reference."""
