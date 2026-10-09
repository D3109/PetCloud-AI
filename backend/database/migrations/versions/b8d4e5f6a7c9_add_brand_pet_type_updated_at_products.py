"""add brand, pet_type and updated_at to products

Revision ID: b8d4e5f6a7c9
Revises: a7c3d4e5f6b8
Create Date: 2026-10-08 23:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b8d4e5f6a7c9'
down_revision: Union[str, Sequence[str], None] = 'a7c3d4e5f6b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('products', sa.Column('brand', sa.String(), nullable=True))
    op.add_column('products', sa.Column('pet_type', sa.String(), nullable=True))
    op.add_column(
        'products',
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('products', 'updated_at')
    op.drop_column('products', 'pet_type')
    op.drop_column('products', 'brand')
