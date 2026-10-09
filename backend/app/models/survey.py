from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Survey(Base):
    """Encuesta de satisfacción (10 preguntas en escala Likert 1-5 + 1
    pregunta abierta de texto libre).

    Las dimensiones corresponden a las variables de la Matriz de
    consistencia del anteproyecto, ampliadas para cubrir todo el ciclo
    de compra (producto, atención, proceso y entrega):
      - Variable independiente (Sistema de Recomendación con IA):
          precision_recomendacion, facilidad_uso, confianza_usuario
      - Variable dependiente (Satisfacción y seguridad de compra):
          nivel_satisfaccion, percepcion_seguridad, intencion_recompra
      - Experiencia de compra end-to-end:
          calidad_productos, atencion_recibida, facilidad_proceso_compra,
          tiempo_entrega

    Las 4 columnas nuevas son nullable a nivel de base de datos para no
    romper encuestas ya respondidas antes de este cambio, pero el
    esquema (SurveyCreate) las exige en toda encuesta nueva.
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

    calidad_productos = Column(Integer, nullable=True)
    atencion_recibida = Column(Integer, nullable=True)
    facilidad_proceso_compra = Column(Integer, nullable=True)
    tiempo_entrega = Column(Integer, nullable=True)

    comentario = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")
