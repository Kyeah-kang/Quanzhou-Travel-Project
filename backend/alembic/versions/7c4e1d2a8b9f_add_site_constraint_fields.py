"""add itinerary constraint fields to heritage_sites

Revision ID: 7c4e1d2a8b9f
Revises: 5a8524575303
Create Date: 2026-09-13

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "7c4e1d2a8b9f"
down_revision: Union[str, Sequence[str], None] = "5a8524575303"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """为世遗点主数据增加行程约束和可信度字段。"""

    op.add_column("heritage_sites", sa.Column("key_element", sa.String(length=50), nullable=True))
    op.add_column(
        "heritage_sites",
        sa.Column("visit_duration_min", sa.Integer(), nullable=True),
    )
    op.add_column("heritage_sites", sa.Column("theme", sa.JSON(), nullable=True))
    op.add_column("heritage_sites", sa.Column("notice", sa.String(length=255), nullable=True))
    op.add_column(
        "heritage_sites",
        sa.Column("fact_status", sa.String(length=20), nullable=True),
    )
    op.add_column(
        "heritage_sites",
        sa.Column("pending_fields", sa.JSON(), nullable=True),
    )


def downgrade() -> None:
    """删除 D14 增加的字段。"""

    op.drop_column("heritage_sites", "pending_fields")
    op.drop_column("heritage_sites", "fact_status")
    op.drop_column("heritage_sites", "notice")
    op.drop_column("heritage_sites", "theme")
    op.drop_column("heritage_sites", "visit_duration_min")
    op.drop_column("heritage_sites", "key_element")
