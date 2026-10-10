"""add incidents table

Revision ID: c3d4e5f6a7b8
Revises: a1b2c3d4e5f6
Create Date: 2026-10-09 20:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'incidents',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('reporter_user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('assigned_to_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('priority', sa.String(), nullable=False, server_default='media'),
        sa.Column('status', sa.String(), nullable=False, server_default='abierto'),
        sa.Column('resolution_notes', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(op.f('ix_incidents_reporter_user_id'), 'incidents', ['reporter_user_id'])
    op.create_index(op.f('ix_incidents_assigned_to_id'), 'incidents', ['assigned_to_id'])
    op.create_index(op.f('ix_incidents_status'), 'incidents', ['status'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_incidents_status'), table_name='incidents')
    op.drop_index(op.f('ix_incidents_assigned_to_id'), table_name='incidents')
    op.drop_index(op.f('ix_incidents_reporter_user_id'), table_name='incidents')
    op.drop_table('incidents')
