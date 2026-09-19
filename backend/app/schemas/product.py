from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.schemas.category import CategoryOut


class ProductCreate(BaseModel):
    name: str
    description: str | None = None
    price: Decimal
    sku: str
    category_ids: list[int] = []


class ProductOut(BaseModel):
    id: int
    name: str
    description: str | None = None
    price: Decimal
    sku: str
    is_active: int
    created_at: datetime
    categories: list[CategoryOut] = []

    model_config = ConfigDict(from_attributes=True)
