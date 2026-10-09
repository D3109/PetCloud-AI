from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.survey import Survey
from app.schemas.survey import SurveyCreate, SurveyStats


def create_survey(db: Session, user_id: int, data: SurveyCreate) -> Survey:
    order_id = data.order_id
    if order_id is not None:
        # Solo se puede asociar la encuesta a un pedido propio; si no es
        # del usuario (o no existe), se guarda la encuesta igual pero sin
        # vincularla a ningun pedido, en vez de fallar la encuesta entera.
        owned_order = (
            db.query(Order)
            .filter(Order.id == order_id, Order.user_id == user_id)
            .first()
        )
        if owned_order is None:
            order_id = None

    # Un cliente responde una sola encuesta por pedido: si ya existe una
    # para este usuario+pedido, se actualiza en vez de crear un duplicado
    # (esta es la regla explicita que permite "modificar" la respuesta).
    existing = None
    if order_id is not None:
        existing = (
            db.query(Survey)
            .filter(Survey.user_id == user_id, Survey.order_id == order_id)
            .first()
        )

    if existing:
        existing.precision_recomendacion = data.precision_recomendacion
        existing.facilidad_uso = data.facilidad_uso
        existing.confianza_usuario = data.confianza_usuario
        existing.nivel_satisfaccion = data.nivel_satisfaccion
        existing.percepcion_seguridad = data.percepcion_seguridad
        existing.intencion_recompra = data.intencion_recompra
        existing.calidad_productos = data.calidad_productos
        existing.atencion_recibida = data.atencion_recibida
        existing.facilidad_proceso_compra = data.facilidad_proceso_compra
        existing.tiempo_entrega = data.tiempo_entrega
        existing.comentario = data.comentario
        db.commit()
        db.refresh(existing)
        return existing

    survey = Survey(
        user_id=user_id,
        order_id=order_id,
        precision_recomendacion=data.precision_recomendacion,
        facilidad_uso=data.facilidad_uso,
        confianza_usuario=data.confianza_usuario,
        nivel_satisfaccion=data.nivel_satisfaccion,
        percepcion_seguridad=data.percepcion_seguridad,
        intencion_recompra=data.intencion_recompra,
        calidad_productos=data.calidad_productos,
        atencion_recibida=data.atencion_recibida,
        facilidad_proceso_compra=data.facilidad_proceso_compra,
        tiempo_entrega=data.tiempo_entrega,
        comentario=data.comentario,
    )
    db.add(survey)
    db.commit()
    db.refresh(survey)
    return survey


def get_recent(db: Session, limit: int = 5) -> list[Survey]:
    """Ultimas encuestas recibidas, para el panel administrativo/dashboard."""
    return db.query(Survey).order_by(Survey.created_at.desc()).limit(limit).all()


def list_surveys(db: Session, skip: int = 0, limit: int = 100) -> list[Survey]:
    return (
        db.query(Survey)
        .order_by(Survey.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_stats(db: Session) -> SurveyStats:
    row = db.query(
        func.count(Survey.id),
        func.avg(Survey.precision_recomendacion),
        func.avg(Survey.facilidad_uso),
        func.avg(Survey.confianza_usuario),
        func.avg(Survey.nivel_satisfaccion),
        func.avg(Survey.percepcion_seguridad),
        func.avg(Survey.intencion_recompra),
        func.avg(Survey.calidad_productos),
        func.avg(Survey.atencion_recibida),
        func.avg(Survey.facilidad_proceso_compra),
        func.avg(Survey.tiempo_entrega),
    ).first()

    total = row[0] or 0

    def avg(value):
        return round(float(value), 2) if value is not None else 0.0

    distribucion_rows = (
        db.query(Survey.nivel_satisfaccion, func.count(Survey.id))
        .group_by(Survey.nivel_satisfaccion)
        .all()
    )
    distribucion_nivel_satisfaccion = {str(k): 0 for k in range(1, 6)}
    for nivel, cantidad in distribucion_rows:
        distribucion_nivel_satisfaccion[str(nivel)] = cantidad

    return SurveyStats(
        total_respuestas=total,
        promedio_precision_recomendacion=avg(row[1]),
        promedio_facilidad_uso=avg(row[2]),
        promedio_confianza_usuario=avg(row[3]),
        promedio_nivel_satisfaccion=avg(row[4]),
        promedio_percepcion_seguridad=avg(row[5]),
        promedio_intencion_recompra=avg(row[6]),
        promedio_calidad_productos=avg(row[7]),
        promedio_atencion_recibida=avg(row[8]),
        promedio_facilidad_proceso_compra=avg(row[9]),
        promedio_tiempo_entrega=avg(row[10]),
        distribucion_nivel_satisfaccion=distribucion_nivel_satisfaccion,
    )
