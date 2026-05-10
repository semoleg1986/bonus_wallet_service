"""Application layer DTOs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

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
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class ListBonusLedgerQuery:
    """Read ledger history with optional filters."""

    parent_id: str | None = None
    reason_code: str | None = None
    operation: str | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    limit: int = 100
    offset: int = 0


@dataclass(frozen=True, slots=True)
class BonusLedgerEntryView:
    """Serializable ledger snapshot."""

    entry_id: str
    parent_id: str
    operation: str
    delta: int
    balance_after: int
    reason_code: str
    reference_id: str | None
    idempotency_key: str | None
    created_at: datetime


@dataclass(frozen=True, slots=True)
class AdminAccountView:
    """Admin-facing wallet snapshot for a parent."""

    parent_id: str
    balance: int
    last_activity_at: datetime | None
    accruals_total: int
    redeemed_total: int
    reverted_total: int
    entries_count: int
    points_unit: str = "bonus_points"


@dataclass(frozen=True, slots=True)
class BonusReasonBreakdownItemView:
    """Aggregated totals for one reason code."""

    reason_code: str
    entries_count: int
    total_delta: int
    total_accrued: int
    total_redeemed: int
    total_reverted: int


@dataclass(frozen=True, slots=True)
class BonusSummaryReportView:
    """High-level reporting snapshot."""

    wallets_with_positive_balance: int
    total_balance_outstanding: int
    total_accrued: int
    total_redeemed: int
    total_reverted: int
    period_from: datetime | None
    period_to: datetime | None


@dataclass(frozen=True, slots=True)
class GetBonusSummaryReportQuery:
    """Read platform-wide bonus summary."""

    date_from: datetime | None = None
    date_to: datetime | None = None


@dataclass(frozen=True, slots=True)
class GetBonusReasonBreakdownQuery:
    """Read reporting breakdown grouped by reason."""

    date_from: datetime | None = None
    date_to: datetime | None = None
    limit: int = 100
    offset: int = 0
