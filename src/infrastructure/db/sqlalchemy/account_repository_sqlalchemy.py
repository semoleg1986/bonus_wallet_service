"""SQLAlchemy account repository."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.domain.wallet.entity import BonusAccount
from src.infrastructure.db.sqlalchemy.models import BonusAccountModel


class SqlAlchemyBonusAccountRepository:
    """Persist bonus accounts via SQLAlchemy."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, parent_id: str) -> BonusAccount | None:
        model = self._session.get(BonusAccountModel, parent_id)
        if model is None:
            return None
        return BonusAccount(
            parent_id=model.parent_id,
            balance=model.balance,
            updated_at=model.updated_at,
        )

    def save(self, account: BonusAccount) -> None:
        model = self._session.get(BonusAccountModel, account.parent_id)
        if model is None:
            model = BonusAccountModel(
                parent_id=account.parent_id,
                balance=account.balance,
                updated_at=account.updated_at,
            )
            self._session.add(model)
            return
        model.balance = account.balance
        model.updated_at = account.updated_at

    def count_positive_balances(self) -> int:
        stmt = select(func.count()).where(BonusAccountModel.balance > 0)
        return int(self._session.execute(stmt).scalar_one() or 0)

    def total_balance_outstanding(self) -> int:
        stmt = select(func.coalesce(func.sum(BonusAccountModel.balance), 0)).where(
            BonusAccountModel.balance > 0
        )
        return int(self._session.execute(stmt).scalar_one() or 0)
