from sqlalchemy.orm import Session

from app.models.promotion import Promotion
from app.schemas.promotion import PromotionCreate


def create_promotion(db: Session, data: PromotionCreate) -> Promotion:
    promotion = Promotion(
        code=data.code.upper(),
        discount_percent=data.discount_percent,
        is_active=True,
    )
    db.add(promotion)
    db.commit()
    db.refresh(promotion)
    return promotion


def list_promotions(db: Session) -> list[Promotion]:
    return db.query(Promotion).all()


def get_active_promotion(db: Session, code: str) -> Promotion | None:
    return db.query(Promotion).filter(
        Promotion.code == code.upper(), Promotion.is_active == True  # noqa: E712
    ).first()
