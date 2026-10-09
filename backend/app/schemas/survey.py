from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SurveyCreate(BaseModel):
    order_id: int | None = None
    precision_recomendacion: int = Field(ge=1, le=5)
    facilidad_uso: int = Field(ge=1, le=5)
    confianza_usuario: int = Field(ge=1, le=5)
    nivel_satisfaccion: int = Field(ge=1, le=5)
    percepcion_seguridad: int = Field(ge=1, le=5)
    intencion_recompra: int = Field(ge=1, le=5)
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
    distribucion_nivel_satisfaccion: dict[str, int] = {}
