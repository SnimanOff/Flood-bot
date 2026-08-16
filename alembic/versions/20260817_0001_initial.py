"""initial

Revision ID: 20260817_0001
Revises:
Create Date: 2026-08-17 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260817_0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("tg_id", sa.BigInteger(), nullable=False),
        sa.Column("username", sa.String(length=255), nullable=True),
        sa.Column("balance", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "role",
            sa.Enum("0", "1", "2", "3", "4", name="role"),
            nullable=False,
            server_default="0",
        ),
        sa.Column("banned_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_query_money", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_tg_id"), "users", ["tg_id"], unique=True)

    op.create_table(
        "money_requests",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_tg_id", sa.BigInteger(), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="pending"),
        sa.Column("caption", sa.Text(), nullable=False),
        sa.Column("photo_file_id", sa.String(length=256), nullable=True),
        sa.Column("notifies", sa.Text(), nullable=False, server_default="[]"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_money_requests_user_tg_id"), "money_requests", ["user_tg_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_money_requests_user_tg_id"), table_name="money_requests")
    op.drop_table("money_requests")
    op.drop_index(op.f("ix_users_tg_id"), table_name="users")
    op.drop_table("users")
    sa.Enum(name="role").drop(op.get_bind(), checkfirst=True)
