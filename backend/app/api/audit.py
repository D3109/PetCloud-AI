from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_admin
from app.models.user import User
from app.schemas.audit import AuditLogOut
from app.services import audit_service

router = APIRouter(prefix="/api/v1/audit", tags=["audit"])


@router.get("", response_model=list[AuditLogOut])
def list_audit_logs(
    skip: int = 0,
    # Tope duro de 500 (sin importar lo que pida el cliente): evita que una
    # tabla de auditoria muy grande se cargue entera en un solo request y
    # consuma memoria/tiempo de ese worker de la API, que es compartido con
    # el resto del sitio.
    limit: int = Query(default=100, le=500, gt=0),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return audit_service.list_audit_logs(db, skip, limit)
