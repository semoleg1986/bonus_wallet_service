"""Repository ports for wallet persistence."""

from __future__ import annotations

from datetime import datetime
from typing import Protocol

from src.application.dto import BonusReasonBreakdownItemView
from src.domain.wallet.entity import BonusAccount, BonusLedgerEntry, LedgerOperation
from src.domain.wallet.rule import BonusRule


class BonusAccountRepositoryPort(Protocol):
    """Storage access for bonus accounts."""

    def get(self, parent_id: str) -> BonusAccount | None:
        """Return wallet account if present."""

    def save(self, account: BonusAccount) -> None:
        """Persist wallet account."""

    def count_positive_balances(self) -> int:
        """Return number of wallets with a positive current balance."""

    def total_balance_outstanding(self) -> int:
        """Return total current positive balance across all wallets."""


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

    def list_by_parent(self, *, parent_id: str) -> list[BonusLedgerEntry]:
        """Return ledger entries for a parent in reverse chronological order."""

    def list_filtered(
        self,
        *,
        parent_id: str | None = None,
        reason_code: str | None = None,
        operation: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[BonusLedgerEntry]:
        """Return ledger entries with optional filters and pagination."""

    def summarize(
        self,
        *,
        parent_id: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> dict[str, int | datetime | None]:
        """Return aggregate totals for filtered ledger entries."""

    def summarize_by_reason(
        self,
        *,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[BonusReasonBreakdownItemView]:
        """Return grouped aggregates by reason code."""


class BonusRuleRepositoryPort(Protocol):
    """Storage access for accrual rules."""

    def get(self, rule_id: str) -> BonusRule | None:
        """Return rule by id."""

    def save(self, rule: BonusRule) -> None:
        """Persist or update a rule."""

    def list(self, *, active_only: bool) -> list[BonusRule]:
        """Return stored rules."""
