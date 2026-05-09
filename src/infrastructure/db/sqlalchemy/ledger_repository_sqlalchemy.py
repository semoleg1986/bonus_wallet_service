"""SQLAlchemy ledger repository."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

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
