"""Repository ports for wallet persistence."""

from __future__ import annotations

from typing import Protocol

from src.domain.wallet.entity import BonusAccount, BonusLedgerEntry, LedgerOperation
from src.domain.wallet.rule import BonusRule


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


class BonusRuleRepositoryPort(Protocol):
    """Storage access for accrual rules."""

    def get(self, rule_id: str) -> BonusRule | None:
        """Return rule by id."""

    def save(self, rule: BonusRule) -> None:
        """Persist or update a rule."""

    def list(self, *, active_only: bool) -> list[BonusRule]:
        """Return stored rules."""
