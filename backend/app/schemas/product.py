from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, field_validator


from app.schemas.category import CategoryOut

PET_TYPES = {"perro", "gato", "ambas", "otro"}


class ProductCreate(BaseModel):
    name: str
    description: str | None = None
    price: Decimal
    sku: str
    image_url: str | None = None
    brand: str | None = None
    pet_type: str | None = None
    category_ids: list[int] = []

    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, v: Decimal) -> Decimal:
        if v < 0:
            raise ValueError("El precio no puede ser negativo")
        return v

    @field_validator("pet_type")
    @classmethod
    def pet_type_must_be_valid(cls, v: str | None) -> str | None:
        if v is not None and v not in PET_TYPES:
            raise ValueError(f"Tipo de mascota invalido. Debe ser uno de {sorted(PET_TYPES)}")
        return v


class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: Decimal | None = None
    image_url: str | None = None
    brand: str | None = None
    pet_type: str | None = None
    is_active: int | None = None
    category_ids: list[int] | None = None

    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, v: Decimal | None) -> Decimal | None:
        if v is not None and v < 0:
            raise ValueError("El precio no puede ser negativo")
        return v

    @field_validator("pet_type")
    @classmethod
    def pet_type_must_be_valid(cls, v: str | None) -> str | None:
        if v is not None and v not in PET_TYPES:
            raise ValueError(f"Tipo de mascota invalido. Debe ser uno de {sorted(PET_TYPES)}")
        return v


class ProductOut(BaseModel):
    id: int
    name: str
    description: str | None = None
    price: Decimal
    sku: str
    image_url: str | None = None
    brand: str | None = None
    pet_type: str | None = None
    is_active: int
    created_at: datetime
    updated_at: datetime | None = None
    categories: list[CategoryOut] = []
    stock_quantity: int = 0

    model_config = ConfigDict(from_attributes=True)
