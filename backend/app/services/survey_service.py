from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.survey import Survey
from app.schemas.survey import SurveyCreate, SurveyStats


def create_survey(db: Session, user_id: int, data: SurveyCreate) -> Survey:
    survey = Survey(
        user_id=user_id,
        order_id=data.order_id,
        precision_recomendacion=data.precision_recomendacion,
        facilidad_uso=data.facilidad_uso,
        confianza_usuario=data.confianza_usuario,
        nivel_satisfaccion=data.nivel_satisfaccion,
        percepcion_seguridad=data.percepcion_seguridad,
        intencion_recompra=data.intencion_recompra,
        comentario=data.comentario,
    )
    db.add(survey)
    db.commit()
    db.refresh(survey)
    return survey


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
    ).first()

    total = row[0] or 0

    def avg(value):
        return round(float(value), 2) if value is not None else 0.0

    return SurveyStats(
        total_respuestas=total,
        promedio_precision_recomendacion=avg(row[1]),
        promedio_facilidad_uso=avg(row[2]),
        promedio_confianza_usuario=avg(row[3]),
        promedio_nivel_satisfaccion=avg(row[4]),
        promedio_percepcion_seguridad=avg(row[5]),
        promedio_intencion_recompra=avg(row[6]),
    )
