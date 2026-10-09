"""add phone and address to users

Revision ID: d0f6a7b8c9e1
Revises: c9e5f6a7b8d0
Create Date: 2026-10-09 07:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd0f6a7b8c9e1'
down_revision: Union[str, Sequence[str], None] = 'c9e5f6a7b8d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('phone', sa.String(), nullable=True))
    op.add_column('users', sa.Column('address', sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'address')
    op.drop_column('users', 'phone')
