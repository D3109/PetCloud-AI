from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.incident import Incident
from app.models.user import User
from app.schemas.incident import IncidentCreate, IncidentUpdate


def _to_dict(incident: Incident) -> dict:
    return {
        "id": incident.id,
        "reporter_user_id": incident.reporter_user_id,
        "reporter_email": incident.reporter.email if incident.reporter else None,
        "assigned_to_id": incident.assigned_to_id,
        "assignee_email": incident.assignee.email if incident.assignee else None,
        "title": incident.title,
        "description": incident.description,
        "priority": incident.priority,
        "status": incident.status,
        "resolution_notes": incident.resolution_notes,
        "created_at": incident.created_at,
        "updated_at": incident.updated_at,
        "resolved_at": incident.resolved_at,
    }


def create_incident(db: Session, reporter: User, incident_in: IncidentCreate) -> dict:
    incident = Incident(
        reporter_user_id=reporter.id,
        title=incident_in.title,
        description=incident_in.description,
        priority=incident_in.priority,
        status="abierto",
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return _to_dict(incident)


def list_incidents(
    db: Session, status: str | None = None, skip: int = 0, limit: int = 100
) -> list[dict]:
    query = db.query(Incident)
    if status:
        query = query.filter(Incident.status == status)
    rows = query.order_by(Incident.created_at.desc()).offset(skip).limit(limit).all()
    return [_to_dict(r) for r in rows]


def list_my_incidents(db: Session, user: User) -> list[dict]:
    rows = (
        db.query(Incident)
        .filter(Incident.reporter_user_id == user.id)
        .order_by(Incident.created_at.desc())
        .all()
    )
    return [_to_dict(r) for r in rows]


def get_incident(db: Session, incident_id: int) -> Incident | None:
    return db.query(Incident).filter(Incident.id == incident_id).first()


def update_incident(db: Session, incident: Incident, update_in: IncidentUpdate) -> dict:
    if update_in.status is not None:
        incident.status = update_in.status
        if update_in.status in ("resuelto", "cerrado") and incident.resolved_at is None:
            incident.resolved_at = datetime.now(timezone.utc)
        elif update_in.status in ("abierto", "en_progreso"):
            incident.resolved_at = None
    if update_in.priority is not None:
        incident.priority = update_in.priority
    if update_in.assigned_to_id is not None:
        incident.assigned_to_id = update_in.assigned_to_id
    if update_in.resolution_notes is not None:
        incident.resolution_notes = update_in.resolution_notes
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return _to_dict(incident)


def incident_stats(db: Session) -> dict:
    rows = db.query(Incident.status, Incident.priority).all()
    by_status: dict[str, int] = {}
    by_priority: dict[str, int] = {}
    for status, priority in rows:
        by_status[status] = by_status.get(status, 0) + 1
        by_priority[priority] = by_priority.get(priority, 0) + 1
    return {
        "total": len(rows),
        "by_status": by_status,
        "by_priority": by_priority,
    }
