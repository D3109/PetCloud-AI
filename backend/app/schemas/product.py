from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


from app.schemas.category import CategoryOut


class ProductCreate(BaseModel):
    name: str
    description: str | None = None
    price: Decimal
    sku: str
    image_url: str | None = None
    category_ids: list[int] = []


class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: Decimal | None = None
    image_url: str | None = None
    is_active: int | None = None
    category_ids: list[int] | None = None


class ProductOut(BaseModel):
    id: int
    name: str
    description: str | None = None
    price: Decimal
    sku: str
    image_url: str | None = None
    is_active: int
    created_at: datetime
    categories: list[CategoryOut] = []

    model_config = ConfigDict(from_attributes=True)
