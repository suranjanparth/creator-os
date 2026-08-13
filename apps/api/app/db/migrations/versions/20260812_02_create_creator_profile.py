"""Create creator profile table.

Revision ID: 20260812_02
Revises: 20260812_01
Create Date: 2026-08-12
"""

from alembic import op
import sqlalchemy as sa


revision = "20260812_02"
down_revision = "20260812_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "creator_profile",
        sa.Column("creator_id", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("handle", sa.String(length=255), nullable=True),
        sa.Column("niche", sa.String(length=255), nullable=True),
        sa.Column("platform", sa.String(length=100), nullable=True),
        sa.Column("audience", sa.String(length=255), nullable=True),
        sa.Column("follower_count", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("creator_id"),
    )


def downgrade() -> None:
    op.drop_table("creator_profile")
