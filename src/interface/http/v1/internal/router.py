"""Internal HTTP API for bonus wallet service."""

from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter, Depends

from src.application.dto import (
    AccrueBonusCommand,
    CommitRedeemCommand,
    GetBalanceQuery,
    RedeemQuoteQuery,
    RevertRedeemCommand,
)
from src.interface.http.common.internal_auth import require_service_token
from src.interface.http.v1.internal.schemas import (
    AccrualRequest,
    AccrualResponse,
    BalanceResponse,
    RedeemCommitRequest,
    RedeemCommitResponse,
    RedeemQuoteRequest,
    RedeemQuoteResponse,
    RedeemRevertRequest,
    RedeemRevertResponse,
)
from src.interface.http.wiring import get_facade

router = APIRouter(prefix="/internal/v1/bonus", tags=["internal"])


@router.get("/balance/{parent_id}", response_model=BalanceResponse)
def get_balance(
    parent_id: str,
    _=Depends(require_service_token),
    facade=Depends(get_facade),
) -> BalanceResponse:
    """Read wallet balance for an internal caller."""

    result = facade.get_balance(GetBalanceQuery(parent_id=parent_id))
    return BalanceResponse(parent_id=result.parent_id, balance=result.balance)


@router.post("/accruals", response_model=AccrualResponse)
def accrue(
    payload: AccrualRequest,
    _=Depends(require_service_token),
    facade=Depends(get_facade),
) -> AccrualResponse:
    """Credit wallet balance."""

    result = facade.accrue(
        AccrueBonusCommand(
            parent_id=payload.parent_id,
            amount=payload.amount,
            reason_code=payload.reason_code,
            reference_id=payload.reference_id,
            idempotency_key=payload.idempotency_key,
        )
    )
    return AccrualResponse(**asdict(result))


@router.post("/redemptions/quote", response_model=RedeemQuoteResponse)
def quote_redeem(
    payload: RedeemQuoteRequest,
    _=Depends(require_service_token),
    facade=Depends(get_facade),
) -> RedeemQuoteResponse:
    """Calculate allowed redemption without mutating state."""

    result = facade.quote_redeem(
        RedeemQuoteQuery(
            parent_id=payload.parent_id,
            requested_amount=payload.requested_amount,
            payment_intent_id=payload.payment_intent_id,
        )
    )
    return RedeemQuoteResponse(**asdict(result))


@router.post("/redemptions/commit", response_model=RedeemCommitResponse)
def commit_redeem(
    payload: RedeemCommitRequest,
    _=Depends(require_service_token),
    facade=Depends(get_facade),
) -> RedeemCommitResponse:
    """Reserve and consume wallet balance for payment."""

    result = facade.commit_redeem(
        CommitRedeemCommand(
            parent_id=payload.parent_id,
            amount=payload.amount,
            payment_intent_id=payload.payment_intent_id,
            idempotency_key=payload.idempotency_key,
        )
    )
    return RedeemCommitResponse(**asdict(result))


@router.post("/redemptions/revert", response_model=RedeemRevertResponse)
def revert_redeem(
    payload: RedeemRevertRequest,
    _=Depends(require_service_token),
    facade=Depends(get_facade),
) -> RedeemRevertResponse:
    """Return consumed wallet balance."""

    result = facade.revert_redeem(
        RevertRedeemCommand(
            parent_id=payload.parent_id,
            amount=payload.amount,
            payment_intent_id=payload.payment_intent_id,
            idempotency_key=payload.idempotency_key,
        )
    )
    return RedeemRevertResponse(**asdict(result))
