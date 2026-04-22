"""add identity account_type and account_status

Revision ID: 004
Revises: 003
Create Date: 2026-04-22

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("identities", sa.Column("account_type", sa.String(20), server_default="anonymous"))
    op.add_column("identities", sa.Column("account_status", sa.String(20), server_default="active"))


def downgrade() -> None:
    op.drop_column("identities", "account_status")
    op.drop_column("identities", "account_type")
