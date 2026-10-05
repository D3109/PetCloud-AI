from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class PromotionCreate(BaseModel):
    code: str
    discount_percent: Decimal


class PromotionOut(BaseModel):
    id: int
    code: str
    discount_percent: Decimal
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
