"""Admin HTTP API for bonus wallet service."""

from __future__ import annotations

import csv
from dataclasses import asdict
from datetime import datetime
from io import StringIO

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response

from src.application.dto import (
    CreateBonusRuleCommand,
    DeactivateBonusRuleCommand,
    GetBonusReasonBreakdownQuery,
    GetBonusSummaryReportQuery,
    ListBonusLedgerQuery,
    ListBonusRulesQuery,
)
from src.interface.http.common.actor import HttpActor, require_admin_actor
from src.interface.http.v1.admin.schemas import (
    AdminBonusAccountResponse,
    AdminBonusLedgerEntryResponse,
    AdminBonusRuleCreateRequest,
    AdminBonusRuleResponse,
    BonusReasonBreakdownItemResponse,
    BonusSummaryReportResponse,
)
from src.interface.http.wiring import get_facade

router = APIRouter(prefix="/v1/admin/bonus", tags=["admin-bonus"])


@router.get("/accounts/{parent_id}", response_model=AdminBonusAccountResponse)
def get_bonus_account(
    parent_id: str,
    _: HttpActor = Depends(require_admin_actor),
    facade=Depends(get_facade),
) -> AdminBonusAccountResponse:
    """Return admin snapshot for one parent wallet."""

    result = facade.get_admin_account(parent_id)
    return AdminBonusAccountResponse(**asdict(result))


@router.get(
    "/accounts/{parent_id}/ledger",
    response_model=list[AdminBonusLedgerEntryResponse],
)
def get_bonus_account_ledger(
    parent_id: str,
    reason_code: str | None = Query(default=None),
    operation: str | None = Query(default=None),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    _: HttpActor = Depends(require_admin_actor),
    facade=Depends(get_facade),
) -> list[AdminBonusLedgerEntryResponse]:
    """Return ledger history for one parent wallet."""

    results = facade.list_ledger(
        ListBonusLedgerQuery(
            parent_id=parent_id,
            reason_code=reason_code,
            operation=operation,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
            offset=offset,
        )
    )
    return [AdminBonusLedgerEntryResponse(**asdict(item)) for item in results]


@router.get("/rules", response_model=list[AdminBonusRuleResponse])
def list_bonus_rules(
    active_only: bool = Query(default=False),
    _: HttpActor = Depends(require_admin_actor),
    facade=Depends(get_facade),
) -> list[AdminBonusRuleResponse]:
    """Return configured bonus rules."""

    results = facade.list_rules(ListBonusRulesQuery(active_only=active_only))
    return [AdminBonusRuleResponse(**asdict(item)) for item in results]


@router.post("/rules", response_model=AdminBonusRuleResponse, status_code=201)
def create_bonus_rule(
    payload: AdminBonusRuleCreateRequest,
    _: HttpActor = Depends(require_admin_actor),
    facade=Depends(get_facade),
) -> AdminBonusRuleResponse:
    """Create a configurable bonus rule."""

    result = facade.create_rule(
        CreateBonusRuleCommand(
            trigger_type=payload.trigger_type,
            threshold=payload.threshold,
            points=payload.points,
        )
    )
    return AdminBonusRuleResponse(**asdict(result))


@router.post("/rules/{rule_id}/deactivate", response_model=AdminBonusRuleResponse)
def deactivate_bonus_rule(
    rule_id: str,
    _: HttpActor = Depends(require_admin_actor),
    facade=Depends(get_facade),
) -> AdminBonusRuleResponse:
    """Deactivate a configurable bonus rule."""

    result = facade.deactivate_rule(DeactivateBonusRuleCommand(rule_id=rule_id))
    return AdminBonusRuleResponse(**asdict(result))


@router.get("/reports/summary", response_model=BonusSummaryReportResponse)
def get_bonus_summary_report(
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    _: HttpActor = Depends(require_admin_actor),
    facade=Depends(get_facade),
) -> BonusSummaryReportResponse:
    """Return aggregate bonus summary."""

    result = facade.get_summary_report(
        GetBonusSummaryReportQuery(date_from=date_from, date_to=date_to)
    )
    return BonusSummaryReportResponse(**asdict(result))


@router.get(
    "/reports/by-reason",
    response_model=list[BonusReasonBreakdownItemResponse],
)
def get_bonus_reason_breakdown(
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    _: HttpActor = Depends(require_admin_actor),
    facade=Depends(get_facade),
) -> list[BonusReasonBreakdownItemResponse]:
    """Return grouped report by reason code."""

    results = facade.get_reason_breakdown(
        GetBonusReasonBreakdownQuery(
            date_from=date_from,
            date_to=date_to,
            limit=limit,
            offset=offset,
        )
    )
    return [BonusReasonBreakdownItemResponse(**asdict(item)) for item in results]


@router.get("/reports/ledger.csv", response_class=Response)
def export_bonus_ledger_csv(
    parent_id: str | None = Query(default=None),
    reason_code: str | None = Query(default=None),
    operation: str | None = Query(default=None),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    _: HttpActor = Depends(require_admin_actor),
    facade=Depends(get_facade),
) -> Response:
    """Export filtered ledger rows as CSV."""

    results = facade.list_ledger(
        ListBonusLedgerQuery(
            parent_id=parent_id,
            reason_code=reason_code,
            operation=operation,
            date_from=date_from,
            date_to=date_to,
            limit=10_000,
            offset=0,
        )
    )

    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "entry_id",
            "parent_id",
            "operation",
            "delta",
            "balance_after",
            "reason_code",
            "reference_id",
            "idempotency_key",
            "created_at",
        ]
    )
    for item in results:
        writer.writerow(
            [
                item.entry_id,
                item.parent_id,
                item.operation,
                item.delta,
                item.balance_after,
                item.reason_code,
                item.reference_id or "",
                item.idempotency_key or "",
                item.created_at.isoformat(),
            ]
        )

    return Response(
        content=buffer.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="bonus-ledger.csv"'},
    )
