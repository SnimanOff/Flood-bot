"""add_checks

Revision ID: 20260818_0004
Revises: 20260817_0003
Create Date: 2026-08-18 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260818_0004"
down_revision: Union[str, Sequence[str], None] = "20260817_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "checks",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_tg_id", sa.BigInteger(), nullable=False),
        sa.Column("good_id", sa.String(length=64), nullable=False),
        sa.Column("good_title", sa.String(length=255), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("qty", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("balance_after", sa.Integer(), nullable=False),
        sa.Column("meta", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_checks_user_tg_id"), "checks", ["user_tg_id"], unique=False)
    op.create_index(op.f("ix_checks_good_id"), "checks", ["good_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_checks_good_id"), table_name="checks")
    op.drop_index(op.f("ix_checks_user_tg_id"), table_name="checks")
    op.drop_table("checks")
