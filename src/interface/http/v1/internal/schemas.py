"""HTTP schemas for internal bonus wallet routes."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from src.domain.wallet.rule import TriggerType


class BalanceResponse(BaseModel):
    parent_id: str
    balance: int = Field(ge=0)


class AccrualRequest(BaseModel):
    parent_id: str
    amount: int = Field(gt=0)
    reason_code: str
    reference_id: str | None = None
    idempotency_key: str | None = None


class AccrualResponse(BaseModel):
    entry_id: str
    parent_id: str
    amount: int = Field(gt=0)
    balance_after: int = Field(ge=0)
    reason_code: str
    reference_id: str | None = None
    idempotency_key: str | None = None
    operation: str


class RedeemQuoteRequest(BaseModel):
    parent_id: str
    requested_amount: int = Field(gt=0)
    payment_intent_id: str


class RedeemQuoteResponse(BaseModel):
    parent_id: str
    requested_amount: int = Field(gt=0)
    available_balance: int = Field(ge=0)
    allowed_amount: int = Field(ge=0)
    payment_intent_id: str


class RedeemCommitRequest(BaseModel):
    parent_id: str
    amount: int = Field(gt=0)
    payment_intent_id: str
    idempotency_key: str | None = None


class RedeemCommitResponse(BaseModel):
    entry_id: str
    parent_id: str
    amount: int = Field(gt=0)
    balance_after: int = Field(ge=0)
    payment_intent_id: str
    idempotency_key: str | None = None
    operation: str


class RedeemRevertRequest(BaseModel):
    parent_id: str
    amount: int = Field(gt=0)
    payment_intent_id: str
    idempotency_key: str | None = None


class RedeemRevertResponse(BaseModel):
    entry_id: str
    parent_id: str
    amount: int = Field(gt=0)
    balance_after: int = Field(ge=0)
    payment_intent_id: str
    idempotency_key: str | None = None
    operation: str


class BonusRuleCreateRequest(BaseModel):
    trigger_type: TriggerType
    threshold: int = Field(gt=0)
    points: int = Field(gt=0)


class BonusRuleResponse(BaseModel):
    rule_id: str
    trigger_type: str
    threshold: int = Field(gt=0)
    points: int = Field(gt=0)
    is_active: bool
    updated_at: datetime


class BonusLedgerEntryResponse(BaseModel):
    entry_id: str
    parent_id: str
    operation: str
    delta: int
    balance_after: int = Field(ge=0)
    reason_code: str
    reference_id: str | None = None
    idempotency_key: str | None = None
    created_at: datetime
