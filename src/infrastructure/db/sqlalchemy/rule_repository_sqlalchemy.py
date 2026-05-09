"""SQLAlchemy bonus rule repository."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.domain.wallet.rule import BonusRule, TriggerType
from src.infrastructure.db.sqlalchemy.models import BonusRuleModel


class SqlAlchemyBonusRuleRepository:
    """Persist bonus rules via SQLAlchemy."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, rule_id: str) -> BonusRule | None:
        model = self._session.get(BonusRuleModel, rule_id)
        return self._to_entity(model)

    def save(self, rule: BonusRule) -> None:
        model = self._session.get(BonusRuleModel, rule.rule_id)
        if model is None:
            model = BonusRuleModel(
                rule_id=rule.rule_id,
                trigger_type=rule.trigger_type.value,
                threshold=rule.threshold,
                points=rule.points,
                is_active=rule.is_active,
                updated_at=rule.updated_at,
            )
            self._session.add(model)
            return
        model.trigger_type = rule.trigger_type.value
        model.threshold = rule.threshold
        model.points = rule.points
        model.is_active = rule.is_active
        model.updated_at = rule.updated_at

    def list(self, *, active_only: bool) -> list[BonusRule]:
        stmt = select(BonusRuleModel)
        if active_only:
            stmt = stmt.where(BonusRuleModel.is_active.is_(True))
        stmt = stmt.order_by(BonusRuleModel.rule_id)
        models = self._session.execute(stmt).scalars().all()
        return [self._to_entity(model) for model in models if model is not None]

    @staticmethod
    def _to_entity(model: BonusRuleModel | None) -> BonusRule | None:
        if model is None:
            return None
        return BonusRule(
            rule_id=model.rule_id,
            trigger_type=TriggerType(model.trigger_type),
            threshold=model.threshold,
            points=model.points,
            is_active=model.is_active,
            updated_at=model.updated_at,
        )
