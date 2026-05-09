"""Bonus accrual rule aggregate."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum

from src.domain.errors import ValidationError


class TriggerType(StrEnum):
    """Supported reward triggers."""

    LESSON_COMPLETED = "lesson_completed"
    COURSE_COMPLETED = "course_completed"
    PAYMENT_CONFIRMED = "payment_confirmed"


@dataclass(slots=True)
class BonusRule:
    """Configurable accrual rule."""

    rule_id: str
    trigger_type: TriggerType
    threshold: int
    points: int
    is_active: bool = True
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def create(
        cls,
        *,
        rule_id: str,
        trigger_type: TriggerType,
        threshold: int,
        points: int,
        updated_at: datetime | None = None,
    ) -> "BonusRule":
        """Create a validated bonus rule."""

        if threshold <= 0:
            raise ValidationError("threshold должен быть > 0.")
        if points <= 0:
            raise ValidationError("points должен быть > 0.")
        return cls(
            rule_id=rule_id,
            trigger_type=trigger_type,
            threshold=threshold,
            points=points,
            updated_at=updated_at or datetime.now(timezone.utc),
        )

    def deactivate(self, *, occurred_at: datetime | None = None) -> None:
        """Deactivate rule without deleting history."""

        self.is_active = False
        self.updated_at = occurred_at or datetime.now(timezone.utc)
