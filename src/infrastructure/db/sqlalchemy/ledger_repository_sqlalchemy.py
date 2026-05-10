"""SQLAlchemy ledger repository."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from src.application.dto import BonusReasonBreakdownItemView
from src.domain.wallet.entity import BonusLedgerEntry, LedgerOperation
from src.infrastructure.db.sqlalchemy.models import BonusLedgerEntryModel


class SqlAlchemyBonusLedgerRepository:
    """Persist ledger entries via SQLAlchemy."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def append(self, entry: BonusLedgerEntry) -> None:
        self._session.add(
            BonusLedgerEntryModel(
                entry_id=entry.entry_id,
                parent_id=entry.parent_id,
                operation=entry.operation.value,
                delta=entry.delta,
                balance_after=entry.balance_after,
                reason_code=entry.reason_code,
                reference_id=entry.reference_id,
                idempotency_key=entry.idempotency_key,
                created_at=entry.created_at,
            )
        )

    def get_by_idempotency(
        self,
        *,
        parent_id: str,
        operation: LedgerOperation,
        idempotency_key: str,
    ) -> BonusLedgerEntry | None:
        stmt = select(BonusLedgerEntryModel).where(
            BonusLedgerEntryModel.parent_id == parent_id,
            BonusLedgerEntryModel.operation == operation.value,
            BonusLedgerEntryModel.idempotency_key == idempotency_key,
        )
        model = self._session.execute(stmt).scalar_one_or_none()
        return self._to_entity(model)

    def get_by_reference(
        self,
        *,
        parent_id: str,
        operation: LedgerOperation,
        reference_id: str,
    ) -> BonusLedgerEntry | None:
        stmt = select(BonusLedgerEntryModel).where(
            BonusLedgerEntryModel.parent_id == parent_id,
            BonusLedgerEntryModel.operation == operation.value,
            BonusLedgerEntryModel.reference_id == reference_id,
        )
        model = self._session.execute(stmt).scalar_one_or_none()
        return self._to_entity(model)

    def list_by_parent(self, *, parent_id: str) -> list[BonusLedgerEntry]:
        return self.list_filtered(parent_id=parent_id)

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
        stmt = select(BonusLedgerEntryModel)
        stmt = self._apply_filters(
            stmt,
            parent_id=parent_id,
            reason_code=reason_code,
            operation=operation,
            date_from=date_from,
            date_to=date_to,
        )
        stmt = (
            stmt.order_by(BonusLedgerEntryModel.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        models = self._session.execute(stmt).scalars().all()
        return [self._to_entity(model) for model in models if model is not None]

    def summarize(
        self,
        *,
        parent_id: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> dict[str, int | datetime | None]:
        stmt = select(
            func.count(BonusLedgerEntryModel.entry_id),
            func.coalesce(
                func.sum(
                    case(
                        (
                            BonusLedgerEntryModel.operation
                            == LedgerOperation.ACCRUAL.value,
                            BonusLedgerEntryModel.delta,
                        ),
                        else_=0,
                    )
                ),
                0,
            ),
            func.coalesce(
                func.sum(
                    case(
                        (
                            BonusLedgerEntryModel.operation
                            == LedgerOperation.REDEEM_COMMIT.value,
                            -BonusLedgerEntryModel.delta,
                        ),
                        else_=0,
                    )
                ),
                0,
            ),
            func.coalesce(
                func.sum(
                    case(
                        (
                            BonusLedgerEntryModel.operation
                            == LedgerOperation.REDEEM_REVERT.value,
                            BonusLedgerEntryModel.delta,
                        ),
                        else_=0,
                    )
                ),
                0,
            ),
            func.max(BonusLedgerEntryModel.created_at),
        )
        stmt = self._apply_filters(
            stmt,
            parent_id=parent_id,
            date_from=date_from,
            date_to=date_to,
        )
        (
            entries_count,
            accruals_total,
            redeemed_total,
            reverted_total,
            last_activity_at,
        ) = self._session.execute(stmt).one()
        return {
            "entries_count": int(entries_count or 0),
            "accruals_total": int(accruals_total or 0),
            "redeemed_total": int(redeemed_total or 0),
            "reverted_total": int(reverted_total or 0),
            "last_activity_at": last_activity_at,
        }

    def summarize_by_reason(
        self,
        *,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[BonusReasonBreakdownItemView]:
        stmt = select(
            BonusLedgerEntryModel.reason_code,
            func.count(BonusLedgerEntryModel.entry_id),
            func.coalesce(func.sum(BonusLedgerEntryModel.delta), 0),
            func.coalesce(
                func.sum(
                    case(
                        (
                            BonusLedgerEntryModel.operation
                            == LedgerOperation.ACCRUAL.value,
                            BonusLedgerEntryModel.delta,
                        ),
                        else_=0,
                    )
                ),
                0,
            ),
            func.coalesce(
                func.sum(
                    case(
                        (
                            BonusLedgerEntryModel.operation
                            == LedgerOperation.REDEEM_COMMIT.value,
                            -BonusLedgerEntryModel.delta,
                        ),
                        else_=0,
                    )
                ),
                0,
            ),
            func.coalesce(
                func.sum(
                    case(
                        (
                            BonusLedgerEntryModel.operation
                            == LedgerOperation.REDEEM_REVERT.value,
                            BonusLedgerEntryModel.delta,
                        ),
                        else_=0,
                    )
                ),
                0,
            ),
        )
        stmt = self._apply_filters(stmt, date_from=date_from, date_to=date_to)
        stmt = (
            stmt.group_by(BonusLedgerEntryModel.reason_code)
            .order_by(
                func.count(BonusLedgerEntryModel.entry_id).desc(),
                BonusLedgerEntryModel.reason_code.asc(),
            )
            .offset(offset)
            .limit(limit)
        )
        rows = self._session.execute(stmt).all()
        return [
            BonusReasonBreakdownItemView(
                reason_code=reason_code,
                entries_count=int(entries_count or 0),
                total_delta=int(total_delta or 0),
                total_accrued=int(total_accrued or 0),
                total_redeemed=int(total_redeemed or 0),
                total_reverted=int(total_reverted or 0),
            )
            for (
                reason_code,
                entries_count,
                total_delta,
                total_accrued,
                total_redeemed,
                total_reverted,
            ) in rows
        ]

    @staticmethod
    def _apply_filters(
        stmt,
        *,
        parent_id: str | None = None,
        reason_code: str | None = None,
        operation: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ):
        if parent_id is not None:
            stmt = stmt.where(BonusLedgerEntryModel.parent_id == parent_id)
        if reason_code is not None:
            stmt = stmt.where(BonusLedgerEntryModel.reason_code == reason_code)
        if operation is not None:
            stmt = stmt.where(BonusLedgerEntryModel.operation == operation)
        if date_from is not None:
            stmt = stmt.where(BonusLedgerEntryModel.created_at >= date_from)
        if date_to is not None:
            stmt = stmt.where(BonusLedgerEntryModel.created_at <= date_to)
        return stmt

    @staticmethod
    def _to_entity(model: BonusLedgerEntryModel | None) -> BonusLedgerEntry | None:
        if model is None:
            return None
        return BonusLedgerEntry(
            entry_id=model.entry_id,
            parent_id=model.parent_id,
            operation=LedgerOperation(model.operation),
            delta=model.delta,
            balance_after=model.balance_after,
            reason_code=model.reason_code,
            reference_id=model.reference_id,
            idempotency_key=model.idempotency_key,
            created_at=model.created_at,
        )
