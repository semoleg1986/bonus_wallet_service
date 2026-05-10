"""HTTP schemas for admin bonus wallet routes."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from src.domain.wallet.rule import TriggerType


class AdminBonusAccountResponse(BaseModel):
    parent_id: str
    balance: int = Field(ge=0)
    last_activity_at: datetime | None = None
    accruals_total: int = Field(ge=0)
    redeemed_total: int = Field(ge=0)
    reverted_total: int = Field(ge=0)
    entries_count: int = Field(ge=0)
    points_unit: str


class AdminBonusLedgerEntryResponse(BaseModel):
    entry_id: str
    parent_id: str
    operation: str
    delta: int
    balance_after: int = Field(ge=0)
    reason_code: str
    reference_id: str | None = None
    idempotency_key: str | None = None
    created_at: datetime


class AdminBonusRuleResponse(BaseModel):
    rule_id: str
    trigger_type: str
    threshold: int = Field(gt=0)
    points: int = Field(gt=0)
    is_active: bool
    updated_at: datetime


class AdminBonusRuleCreateRequest(BaseModel):
    trigger_type: TriggerType
    threshold: int = Field(gt=0)
    points: int = Field(gt=0)


class BonusSummaryReportResponse(BaseModel):
    wallets_with_positive_balance: int = Field(ge=0)
    total_balance_outstanding: int = Field(ge=0)
    total_accrued: int = Field(ge=0)
    total_redeemed: int = Field(ge=0)
    total_reverted: int = Field(ge=0)
    period_from: datetime | None = None
    period_to: datetime | None = None


class BonusReasonBreakdownItemResponse(BaseModel):
    reason_code: str
    entries_count: int = Field(ge=0)
    total_delta: int
    total_accrued: int = Field(ge=0)
    total_redeemed: int = Field(ge=0)
    total_reverted: int = Field(ge=0)
