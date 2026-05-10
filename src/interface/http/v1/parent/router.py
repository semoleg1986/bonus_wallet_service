"""Parent HTTP API for bonus wallet service."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime

from fastapi import APIRouter, Depends, Query

from src.application.dto import GetBalanceQuery, ListBonusLedgerQuery
from src.interface.http.common.actor import HttpActor, require_parent_actor
from src.interface.http.v1.parent.schemas import (
    ParentBonusBalanceResponse,
    ParentBonusLedgerEntryResponse,
)
from src.interface.http.wiring import get_facade

router = APIRouter(prefix="/v1/parent/bonus", tags=["parent-bonus"])


@router.get("/balance", response_model=ParentBonusBalanceResponse)
def get_parent_bonus_balance(
    actor: HttpActor = Depends(require_parent_actor),
    facade=Depends(get_facade),
) -> ParentBonusBalanceResponse:
    """Return current parent bonus balance."""

    result = facade.get_balance(GetBalanceQuery(parent_id=actor.actor_id))
    return ParentBonusBalanceResponse(**asdict(result))


@router.get("/ledger", response_model=list[ParentBonusLedgerEntryResponse])
def list_parent_bonus_ledger(
    reason_code: str | None = Query(default=None),
    operation: str | None = Query(default=None),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    actor: HttpActor = Depends(require_parent_actor),
    facade=Depends(get_facade),
) -> list[ParentBonusLedgerEntryResponse]:
    """Return ledger history for the authenticated parent."""

    results = facade.list_ledger(
        ListBonusLedgerQuery(
            parent_id=actor.actor_id,
            reason_code=reason_code,
            operation=operation,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
            offset=offset,
        )
    )
    return [ParentBonusLedgerEntryResponse(**asdict(item)) for item in results]
