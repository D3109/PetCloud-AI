from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_admin
from app.models.user import User
from app.schemas.survey import SurveyCreate, SurveyOut, SurveyStats
from app.services import survey_service

router = APIRouter(prefix="/api/v1/surveys", tags=["surveys"])


@router.post("", response_model=SurveyOut, status_code=201)
def create_survey(
    data: SurveyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return survey_service.create_survey(db, current_user.id, data)


@router.get("", response_model=list[SurveyOut])
def list_surveys(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return survey_service.list_surveys(db, skip, limit)


@router.get("/stats", response_model=SurveyStats)
def survey_stats(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return survey_service.get_stats(db)
