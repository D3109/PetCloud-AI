"""add calidad_productos, atencion_recibida, facilidad_proceso_compra,
tiempo_entrega to surveys (ampliar encuesta a 10 preguntas)

Revision ID: e2a7b8c9d0f1
Revises: d0f6a7b8c9e1
Create Date: 2026-10-09 08:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e2a7b8c9d0f1'
down_revision: Union[str, Sequence[str], None] = 'd0f6a7b8c9e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('surveys', sa.Column('calidad_productos', sa.Integer(), nullable=True))
    op.add_column('surveys', sa.Column('atencion_recibida', sa.Integer(), nullable=True))
    op.add_column('surveys', sa.Column('facilidad_proceso_compra', sa.Integer(), nullable=True))
    op.add_column('surveys', sa.Column('tiempo_entrega', sa.Integer(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('surveys', 'tiempo_entrega')
    op.drop_column('surveys', 'facilidad_proceso_compra')
    op.drop_column('surveys', 'atencion_recibida')
    op.drop_column('surveys', 'calidad_productos')
