from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class CartItemAdd(BaseModel):
    product_id: int
    quantity: int = 1


class CartItemQuantityUpdate(BaseModel):
    quantity: int


class CartItemOut(BaseModel):
    id: int
    product_id: int
    product_name: str
    unit_price: Decimal
    quantity: int
    subtotal: Decimal

    model_config = ConfigDict(from_attributes=True)


class CartOut(BaseModel):
    id: int
    items: list[CartItemOut]
    total: Decimal
