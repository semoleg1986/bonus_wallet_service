"""Wallet aggregate and ledger entities."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum

from src.domain.errors import InvariantViolationError, ValidationError


class LedgerOperation(StrEnum):
    """Supported ledger operation types."""

    ACCRUAL = "accrual"
    REDEEM_COMMIT = "redeem_commit"
    REDEEM_REVERT = "redeem_revert"


@dataclass(slots=True, frozen=True)
class BonusLedgerEntry:
    """Append-only bonus ledger record."""

    entry_id: str
    parent_id: str
    operation: LedgerOperation
    delta: int
    balance_after: int
    reason_code: str
    reference_id: str | None
    idempotency_key: str | None
    created_at: datetime

    @classmethod
    def create(
        cls,
        *,
        entry_id: str,
        parent_id: str,
        operation: LedgerOperation,
        delta: int,
        balance_after: int,
        reason_code: str,
        reference_id: str | None,
        idempotency_key: str | None,
        created_at: datetime | None = None,
    ) -> "BonusLedgerEntry":
        """Build a validated ledger entry."""

        if not parent_id.strip():
            raise ValidationError("parent_id обязателен.")
        if delta == 0:
            raise ValidationError("delta не может быть нулевым.")
        if balance_after < 0:
            raise InvariantViolationError("Баланс после операции не может быть < 0.")
        if not reason_code.strip():
            raise ValidationError("reason_code обязателен.")
        return cls(
            entry_id=entry_id,
            parent_id=parent_id,
            operation=operation,
            delta=delta,
            balance_after=balance_after,
            reason_code=reason_code,
            reference_id=reference_id,
            idempotency_key=idempotency_key,
            created_at=created_at or datetime.now(timezone.utc),
        )


@dataclass(slots=True)
class BonusAccount:
    """Wallet aggregate for a parent loyalty balance."""

    parent_id: str
    balance: int = 0
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def create(cls, parent_id: str) -> "BonusAccount":
        """Create an empty wallet account."""

        if not parent_id.strip():
            raise ValidationError("parent_id обязателен.")
        return cls(parent_id=parent_id)

    def accrue(self, amount: int, *, occurred_at: datetime | None = None) -> int:
        """Increase balance by a positive amount."""

        if amount <= 0:
            raise ValidationError("amount должен быть > 0.")
        self.balance += amount
        self.updated_at = occurred_at or datetime.now(timezone.utc)
        return self.balance

    def redeem(self, amount: int, *, occurred_at: datetime | None = None) -> int:
        """Decrease balance for bonus redemption."""

        if amount <= 0:
            raise ValidationError("amount должен быть > 0.")
        if amount > self.balance:
            raise InvariantViolationError("Недостаточно бонусного баланса.")
        self.balance -= amount
        self.updated_at = occurred_at or datetime.now(timezone.utc)
        return self.balance
