"""add auth_provider and google_sub to users (Google login)

Revision ID: c9e5f6a7b8d0
Revises: b8d4e5f6a7c9
Create Date: 2026-10-08 23:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c9e5f6a7b8d0'
down_revision: Union[str, Sequence[str], None] = 'b8d4e5f6a7c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'users',
        sa.Column('auth_provider', sa.String(), nullable=False, server_default='local'),
    )
    op.alter_column('users', 'auth_provider', server_default=None)
    op.add_column('users', sa.Column('google_sub', sa.String(), nullable=True))
    op.create_index(op.f('ix_users_google_sub'), 'users', ['google_sub'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_users_google_sub'), table_name='users')
    op.drop_column('users', 'google_sub')
    op.drop_column('users', 'auth_provider')
