from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SurveyCreate(BaseModel):
    order_id: int | None = None

    # Sistema de recomendacion con IA
    precision_recomendacion: int = Field(ge=1, le=5)
    facilidad_uso: int = Field(ge=1, le=5)
    confianza_usuario: int = Field(ge=1, le=5)

    # Satisfaccion y seguridad de compra
    nivel_satisfaccion: int = Field(ge=1, le=5)
    percepcion_seguridad: int = Field(ge=1, le=5)
    intencion_recompra: int = Field(ge=1, le=5)

    # Experiencia de compra end-to-end
    calidad_productos: int = Field(ge=1, le=5)
    atencion_recibida: int = Field(ge=1, le=5)
    facilidad_proceso_compra: int = Field(ge=1, le=5)
    tiempo_entrega: int = Field(ge=1, le=5)

    # Pregunta abierta (opcional)
    comentario: str | None = None


class SurveyOut(BaseModel):
    id: int
    user_id: int
    order_id: int | None = None
    precision_recomendacion: int
    facilidad_uso: int
    confianza_usuario: int
    nivel_satisfaccion: int
    percepcion_seguridad: int
    intencion_recompra: int
    calidad_productos: int | None = None
    atencion_recibida: int | None = None
    facilidad_proceso_compra: int | None = None
    tiempo_entrega: int | None = None
    comentario: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SurveyStats(BaseModel):
    total_respuestas: int
    promedio_precision_recomendacion: float
    promedio_facilidad_uso: float
    promedio_confianza_usuario: float
    promedio_nivel_satisfaccion: float
    promedio_percepcion_seguridad: float
    promedio_intencion_recompra: float
    promedio_calidad_productos: float
    promedio_atencion_recibida: float
    promedio_facilidad_proceso_compra: float
    promedio_tiempo_entrega: float
    distribucion_nivel_satisfaccion: dict[str, int] = {}
