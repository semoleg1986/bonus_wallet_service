"""Application layer DTOs."""

from __future__ import annotations

from dataclasses import dataclass

from src.domain.wallet.rule import TriggerType


@dataclass(frozen=True, slots=True)
class GetBalanceQuery:
    """Read current wallet balance."""

    parent_id: str


@dataclass(frozen=True, slots=True)
class AccrueBonusCommand:
    """Credit bonus balance."""

    parent_id: str
    amount: int
    reason_code: str
    reference_id: str | None = None
    idempotency_key: str | None = None


@dataclass(frozen=True, slots=True)
class RedeemQuoteQuery:
    """Calculate redeemable amount without mutation."""

    parent_id: str
    requested_amount: int
    payment_intent_id: str


@dataclass(frozen=True, slots=True)
class CommitRedeemCommand:
    """Consume bonus balance for a payment."""

    parent_id: str
    amount: int
    payment_intent_id: str
    idempotency_key: str | None = None


@dataclass(frozen=True, slots=True)
class RevertRedeemCommand:
    """Return previously committed bonus balance."""

    parent_id: str
    amount: int
    payment_intent_id: str
    idempotency_key: str | None = None


@dataclass(frozen=True, slots=True)
class BalanceView:
    """Wallet balance snapshot."""

    parent_id: str
    balance: int


@dataclass(frozen=True, slots=True)
class AccrualView:
    """Result of bonus accrual."""

    entry_id: str
    parent_id: str
    amount: int
    balance_after: int
    reason_code: str
    reference_id: str | None
    idempotency_key: str | None
    operation: str


@dataclass(frozen=True, slots=True)
class RedeemQuoteView:
    """Result of redemption quote calculation."""

    parent_id: str
    requested_amount: int
    available_balance: int
    allowed_amount: int
    payment_intent_id: str


@dataclass(frozen=True, slots=True)
class RedemptionView:
    """Result of redeem commit or revert."""

    entry_id: str
    parent_id: str
    amount: int
    balance_after: int
    payment_intent_id: str
    idempotency_key: str | None
    operation: str


@dataclass(frozen=True, slots=True)
class CreateBonusRuleCommand:
    """Create a new accrual rule."""

    trigger_type: TriggerType
    threshold: int
    points: int


@dataclass(frozen=True, slots=True)
class DeactivateBonusRuleCommand:
    """Deactivate an existing accrual rule."""

    rule_id: str


@dataclass(frozen=True, slots=True)
class ListBonusRulesQuery:
    """Read configured bonus rules."""

    active_only: bool = False


@dataclass(frozen=True, slots=True)
class BonusRuleView:
    """Serializable rule snapshot."""

    rule_id: str
    trigger_type: str
    threshold: int
    points: int
    is_active: bool
