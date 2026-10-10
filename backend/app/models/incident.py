from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Incident(Base):
    """Incidente de servicio TI: algo que un cliente o un miembro del staff
    reporta como roto o que no funciona como debería (ej. "no me llega el
    correo de confirmación", "el pago quedó en estado pendiente"). Sigue un
    ciclo simple de estados: abierto -> en_progreso -> resuelto -> cerrado."""

    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    reporter_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    priority = Column(String, nullable=False, default="media")  # baja, media, alta, critica
    status = Column(String, nullable=False, default="abierto", index=True)  # abierto, en_progreso, resuelto, cerrado
    resolution_notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    reporter = relationship("User", foreign_keys=[reporter_user_id])
    assignee = relationship("User", foreign_keys=[assigned_to_id])
