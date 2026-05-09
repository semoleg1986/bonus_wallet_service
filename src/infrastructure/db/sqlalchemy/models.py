"""SQLAlchemy models for bonus wallet service."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.db.sqlalchemy.base import Base


class BonusAccountModel(Base):
    """Stored wallet account aggregate snapshot."""

    __tablename__ = "bonus_accounts"

    parent_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    balance: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )


class BonusLedgerEntryModel(Base):
    """Stored append-only ledger entry."""

    __tablename__ = "bonus_ledger"
    __table_args__ = (
        UniqueConstraint(
            "parent_id",
            "operation",
            "idempotency_key",
            name="uq_bonus_ledger_parent_operation_idempotency",
        ),
        UniqueConstraint(
            "parent_id",
            "operation",
            "reference_id",
            name="uq_bonus_ledger_parent_operation_reference",
        ),
    )

    entry_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    parent_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    operation: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    delta: Mapped[int] = mapped_column(Integer, nullable=False)
    balance_after: Mapped[int] = mapped_column(Integer, nullable=False)
    reason_code: Mapped[str] = mapped_column(String(64), nullable=False)
    reference_id: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
        index=True,
    )
    idempotency_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
