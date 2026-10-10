from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_support
from app.models.user import User
from app.schemas.incident import IncidentCreate, IncidentOut, IncidentUpdate
from app.services import incident_service

router = APIRouter(prefix="/api/v1/incidents", tags=["incidents"])


@router.post("", response_model=IncidentOut, status_code=201)
def create_incident(
    incident_in: IncidentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cualquier usuario logueado (cliente o staff) puede reportar un incidente."""
    return incident_service.create_incident(db, current_user, incident_in)


@router.get("/mine", response_model=list[IncidentOut])
def list_my_incidents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Los incidentes que el propio usuario ha reportado."""
    return incident_service.list_my_incidents(db, current_user)


@router.get("", response_model=list[IncidentOut])
def list_incidents(
    status: str | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: User = Depends(require_support),
):
    """Listado completo, para atención al cliente/admin/root. Filtra por status opcionalmente."""
    return incident_service.list_incidents(db, status, skip, limit)


@router.get("/stats")
def incident_stats(
    db: Session = Depends(get_db),
    _: User = Depends(require_support),
):
    """Conteos por estado y prioridad, para el tablero de KPIs."""
    return incident_service.incident_stats(db)


@router.patch("/{incident_id}", response_model=IncidentOut)
def update_incident(
    incident_id: int,
    update_in: IncidentUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_support),
):
    """Cambiar estado, prioridad, asignación o notas de resolución."""
    incident = incident_service.get_incident(db, incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incidente no encontrado")
    return incident_service.update_incident(db, incident, update_in)
