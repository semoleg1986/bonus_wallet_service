"""create bonus wallet tables

Revision ID: 20260509_0001
Revises:
Create Date: 2026-05-09
"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "20260509_0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "bonus_accounts",
        sa.Column("parent_id", sa.String(length=64), primary_key=True),
        sa.Column("balance", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "bonus_ledger",
        sa.Column("entry_id", sa.String(length=64), primary_key=True),
        sa.Column("parent_id", sa.String(length=64), nullable=False),
        sa.Column("operation", sa.String(length=32), nullable=False),
        sa.Column("delta", sa.Integer(), nullable=False),
        sa.Column("balance_after", sa.Integer(), nullable=False),
        sa.Column("reason_code", sa.String(length=64), nullable=False),
        sa.Column("reference_id", sa.String(length=128), nullable=True),
        sa.Column("idempotency_key", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "parent_id",
            "operation",
            "idempotency_key",
            name="uq_bonus_ledger_parent_operation_idempotency",
        ),
        sa.UniqueConstraint(
            "parent_id",
            "operation",
            "reference_id",
            name="uq_bonus_ledger_parent_operation_reference",
        ),
    )
    op.create_index(
        "ix_bonus_ledger_parent_id",
        "bonus_ledger",
        ["parent_id"],
        unique=False,
    )
    op.create_index(
        "ix_bonus_ledger_operation",
        "bonus_ledger",
        ["operation"],
        unique=False,
    )
    op.create_index(
        "ix_bonus_ledger_reference_id",
        "bonus_ledger",
        ["reference_id"],
        unique=False,
    )
    op.create_index(
        "ix_bonus_ledger_idempotency_key",
        "bonus_ledger",
        ["idempotency_key"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_bonus_ledger_idempotency_key", table_name="bonus_ledger")
    op.drop_index("ix_bonus_ledger_reference_id", table_name="bonus_ledger")
    op.drop_index("ix_bonus_ledger_operation", table_name="bonus_ledger")
    op.drop_index("ix_bonus_ledger_parent_id", table_name="bonus_ledger")
    op.drop_table("bonus_ledger")
    op.drop_table("bonus_accounts")
