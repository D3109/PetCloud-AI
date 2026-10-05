from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_admin
from app.models.user import User
from app.schemas.promotion import PromotionCreate, PromotionOut
from app.services import promotion_service

router = APIRouter(prefix="/api/v1/promotions", tags=["promotions"])


@router.post("", response_model=PromotionOut, status_code=201)
def create_promotion(
    data: PromotionCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return promotion_service.create_promotion(db, data)


@router.get("", response_model=list[PromotionOut])
def list_promotions(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return promotion_service.list_promotions(db)
