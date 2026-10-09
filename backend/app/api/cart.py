from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.cart import CartItemAdd, CartItemQuantityUpdate, CartOut
from app.services import cart_service

router = APIRouter(prefix="/api/v1/cart", tags=["cart"])


@router.get("", response_model=CartOut)
def get_cart(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cart = cart_service.get_or_create_cart(db, current_user.id)
    return cart_service.to_out_dict(cart)


@router.post("/items", response_model=CartOut, status_code=201)
def add_item(
    data: CartItemAdd,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        cart = cart_service.add_item(db, current_user.id, data.product_id, data.quantity)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return cart_service.to_out_dict(cart)


@router.patch("/items/{product_id}", response_model=CartOut)
def update_item_quantity(
    product_id: int,
    data: CartItemQuantityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        cart = cart_service.update_item_quantity(db, current_user.id, product_id, data.quantity)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return cart_service.to_out_dict(cart)


@router.delete("/items/{product_id}", response_model=CartOut)
def remove_item(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        cart = cart_service.remove_item(db, current_user.id, product_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return cart_service.to_out_dict(cart)
