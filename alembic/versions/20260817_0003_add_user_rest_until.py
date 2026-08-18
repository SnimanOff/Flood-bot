"""add_user_rest_until

Revision ID: 20260817_0003
Revises: 20260817_0002
Create Date: 2026-08-17 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260817_0003"
down_revision: Union[str, Sequence[str], None] = "20260817_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("rest_until", sa.Date(), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "rest_until")