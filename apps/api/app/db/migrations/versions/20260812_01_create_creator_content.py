"""Create creator content table.

Revision ID: 20260812_01
Revises:
Create Date: 2026-08-12
"""

from alembic import op
import sqlalchemy as sa


revision = "20260812_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "creator_content",
        sa.Column("id", sa.String(length=255), nullable=False),
        sa.Column("creator_id", sa.String(length=255), nullable=False),
        sa.Column("platform", sa.String(length=100), nullable=False),
        sa.Column("url", sa.String(length=500), nullable=True),
        sa.Column("content_type", sa.String(length=100), nullable=False),
        sa.Column("category", sa.String(length=255), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("views", sa.Integer(), nullable=True),
        sa.Column("likes", sa.Integer(), nullable=True),
        sa.Column("comments", sa.Integer(), nullable=True),
        sa.Column("shares", sa.Integer(), nullable=True),
        sa.Column("saves", sa.Integer(), nullable=True),
        sa.Column("reach", sa.Integer(), nullable=True),
        sa.Column("impressions", sa.Integer(), nullable=True),
        sa.Column("engagement_rate", sa.Float(), nullable=True),
        sa.Column("published_at", sa.Date(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_creator_content_creator_id", "creator_content", ["creator_id"])


def downgrade() -> None:
    op.drop_index("ix_creator_content_creator_id", table_name="creator_content")
    op.drop_table("creator_content")
