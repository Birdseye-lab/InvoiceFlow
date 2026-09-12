"""create clients table

Revision ID: b43a1b886771
Revises:
Create Date: 2026-09-06 11:44:30.806598

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b43a1b886771"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "clients",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )


def downgrade() -> None:
    op.drop_table("clients")