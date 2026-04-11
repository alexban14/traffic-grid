"""initial schema

Revision ID: 001
Revises: None
Create Date: 2026-04-11

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "identities",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("username", sa.String(255), nullable=True),
        sa.Column("platform", sa.String(50), nullable=True),
        sa.Column("status", sa.String(20), server_default="active", nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("screen_resolution", sa.String(20), nullable=True),
        sa.Column("behavioral_dna", Vector(1536), nullable=True),
        sa.Column("trust_score", sa.Integer(), server_default="50", nullable=True),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
    )
    op.create_index("ix_identities_username", "identities", ["username"])

    op.create_table(
        "workers",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("type", sa.String(50), nullable=True),
        sa.Column("status", sa.String(20), server_default="IDLE", nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("last_heartbeat", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "proxies",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("port", sa.Integer(), nullable=True),
        sa.Column("protocol", sa.String(10), server_default="socks5", nullable=True),
        sa.Column("provider", sa.String(50), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=True),
        sa.Column("last_rotated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("type", sa.String(50), nullable=True),
        sa.Column("target_url", sa.Text(), nullable=True),
        sa.Column("status", sa.String(20), server_default="PENDING", nullable=True),
        sa.Column("config", sa.JSON(), nullable=True),
        sa.Column("celery_task_id", sa.String(255), nullable=True),
        sa.Column("worker_id", sa.Integer(), sa.ForeignKey("workers.id"), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("result", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("tasks")
    op.drop_table("proxies")
    op.drop_table("workers")
    op.drop_index("ix_identities_username", table_name="identities")
    op.drop_table("identities")
