"""index audit_logs created_at

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-10-19 20:56:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4e5f6a7b8c9'
down_revision: Union[str, Sequence[str], None] = 'c3d4e5f6a7b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema.

    audit_logs se consulta siempre con ORDER BY created_at DESC + LIMIT
    (ver audit_service.list_audit_logs). Sin indice, esa consulta hace un
    seq scan + sort completo de la tabla cada vez; con tablas chicas no se
    nota, pero si la auditoria crece mucho (miles/millones de filas) se
    vuelve lenta y le pega a la misma base de datos que usa el resto del
    sitio. El indice mantiene esa consulta rapida sin importar que tan
    grande crezca la tabla.
    """
    op.create_index(op.f('ix_audit_logs_created_at'), 'audit_logs', ['created_at'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_audit_logs_created_at'), table_name='audit_logs')
