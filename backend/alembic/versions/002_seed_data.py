"""seed initial data

Revision ID: 002
Revises: 001
Create Date: 2026-04-11

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        INSERT INTO proxies (ip_address, port, protocol, provider, is_active)
        VALUES ('192.168.1.100', 8080, 'socks5', 'Digi RO', true),
               ('192.168.1.101', 8080, 'socks5', 'Orange RO', true)
        ON CONFLICT DO NOTHING
    """)
    op.execute("""
        INSERT INTO identities (username, platform, status, user_agent, trust_score)
        VALUES ('alex_tiktok_01', 'tiktok', 'active', 'Mozilla/5.0 (Linux; Android 14; SM-S928B)', 85),
               ('alex_yt_01', 'youtube', 'active', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', 90)
        ON CONFLICT (username) DO NOTHING
    """)


def downgrade() -> None:
    op.execute("DELETE FROM identities WHERE username IN ('alex_tiktok_01', 'alex_yt_01')")
    op.execute("DELETE FROM proxies WHERE provider IN ('Digi RO', 'Orange RO')")
