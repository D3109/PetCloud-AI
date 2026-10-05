from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.payment import PaymentCreate, PaymentOut
from app.services import payment_service

router = APIRouter(prefix="/api/v1/payments", tags=["payments"])


@router.post("/{order_id}", response_model=PaymentOut, status_code=201)
def pay_order(
    order_id: int,
    data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return payment_service.pay_order(db, current_user.id, order_id, data.method)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
