from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Survey(Base):
    """Encuesta de satisfacción (escala Likert 1-5).

    Las dimensiones corresponden a las variables de la Matriz de
    consistencia del anteproyecto:
      - Variable independiente (Sistema de Recomendación con IA):
          precision_recomendacion, facilidad_uso, confianza_usuario
      - Variable dependiente (Satisfacción y seguridad de compra):
          nivel_satisfaccion, percepcion_seguridad, intencion_recompra
    """

    __tablename__ = "surveys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)

    precision_recomendacion = Column(Integer, nullable=False)
    facilidad_uso = Column(Integer, nullable=False)
    confianza_usuario = Column(Integer, nullable=False)

    nivel_satisfaccion = Column(Integer, nullable=False)
    percepcion_seguridad = Column(Integer, nullable=False)
    intencion_recompra = Column(Integer, nullable=False)

    comentario = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")
