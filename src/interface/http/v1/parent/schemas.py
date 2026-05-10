"""HTTP schemas for parent bonus wallet routes."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ParentBonusBalanceResponse(BaseModel):
    parent_id: str
    balance: int = Field(ge=0)


class ParentBonusLedgerEntryResponse(BaseModel):
    entry_id: str
    parent_id: str
    operation: str
    delta: int
    balance_after: int = Field(ge=0)
    reason_code: str
    reference_id: str | None = None
    created_at: datetime
