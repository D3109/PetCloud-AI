from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class OrderItemOut(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    unit_price: Decimal

    model_config = ConfigDict(from_attributes=True)


class CheckoutRequest(BaseModel):
    promotion_code: str | None = None


class OrderOut(BaseModel):
    id: int
    status: str
    subtotal_amount: Decimal
    discount_amount: Decimal
    total_amount: Decimal
    promotion_code: str | None = None
    created_at: datetime
    items: list[OrderItemOut]

    model_config = ConfigDict(from_attributes=True)
