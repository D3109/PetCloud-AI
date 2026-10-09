"""add surveys table

Revision ID: e1a2b3c4d5f6
Revises: cb4f88ab0edb
Create Date: 2026-10-08 20:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e1a2b3c4d5f6'
down_revision: Union[str, Sequence[str], None] = 'cb4f88ab0edb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'surveys',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=True),
        sa.Column('precision_recomendacion', sa.Integer(), nullable=False),
        sa.Column('facilidad_uso', sa.Integer(), nullable=False),
        sa.Column('confianza_usuario', sa.Integer(), nullable=False),
        sa.Column('nivel_satisfaccion', sa.Integer(), nullable=False),
        sa.Column('percepcion_seguridad', sa.Integer(), nullable=False),
        sa.Column('intencion_recompra', sa.Integer(), nullable=False),
        sa.Column('comentario', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_surveys_id'), 'surveys', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_surveys_id'), table_name='surveys')
    op.drop_table('surveys')
