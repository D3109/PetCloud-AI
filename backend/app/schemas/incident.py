from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator

PRIORIDADES_VALIDAS = {"baja", "media", "alta", "critica"}
ESTADOS_VALIDOS = {"abierto", "en_progreso", "resuelto", "cerrado"}


class IncidentCreate(BaseModel):
    title: str
    description: str
    priority: str = "media"

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("El título del incidente no puede estar vacío")
        return v

    @field_validator("description")
    @classmethod
    def description_must_not_be_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("La descripción del incidente no puede estar vacía")
        return v

    @field_validator("priority")
    @classmethod
    def priority_must_be_valid(cls, v: str) -> str:
        v = v.strip().lower()
        if v not in PRIORIDADES_VALIDAS:
            raise ValueError("priority debe ser 'baja', 'media', 'alta' o 'critica'")
        return v


class IncidentUpdate(BaseModel):
    status: str | None = None
    priority: str | None = None
    assigned_to_id: int | None = None
    resolution_notes: str | None = None

    @field_validator("status")
    @classmethod
    def status_must_be_valid(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip().lower()
        if v not in ESTADOS_VALIDOS:
            raise ValueError("status debe ser 'abierto', 'en_progreso', 'resuelto' o 'cerrado'")
        return v

    @field_validator("priority")
    @classmethod
    def priority_must_be_valid(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip().lower()
        if v not in PRIORIDADES_VALIDAS:
            raise ValueError("priority debe ser 'baja', 'media', 'alta' o 'critica'")
        return v


class IncidentOut(BaseModel):
    id: int
    reporter_user_id: int | None = None
    reporter_email: str | None = None
    assigned_to_id: int | None = None
    assignee_email: str | None = None
    title: str
    description: str
    priority: str
    status: str
    resolution_notes: str | None = None
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
