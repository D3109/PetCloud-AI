from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_support
from app.models.user import User
from app.schemas.order import CheckoutRequest, OrderOut
from app.services import order_service

router = APIRouter(prefix="/api/v1/orders", tags=["orders"])


@router.post("/checkout", response_model=OrderOut, status_code=201)
def checkout(
    data: CheckoutRequest = CheckoutRequest(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        order = order_service.checkout(db, current_user.id, data.promotion_code)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return order_service.to_out_dict(order)


@router.get("", response_model=list[OrderOut])
def list_orders(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    orders = order_service.list_orders(db, current_user.id)
    return [order_service.to_out_dict(o) for o in orders]


@router.get("/admin", response_model=list[OrderOut])
def list_orders_admin(
    skip: int = 0,
    limit: int = 100,
    status: str | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(require_support),
):
    """Listado de TODOS los pedidos, para admin/root/atencion_cliente."""
    orders = order_service.list_all_orders(db, skip, limit, status)
    return [order_service.to_out_dict(o, include_user=True) for o in orders]


@router.get("/admin/{order_id}", response_model=OrderOut)
def get_order_admin(
    order_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_support),
):
    order = order_service.get_any_order(db, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order_service.to_out_dict(order, include_user=True)


@router.get("/{order_id}", response_model=OrderOut)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = order_service.get_order(db, current_user.id, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order_service.to_out_dict(order)
