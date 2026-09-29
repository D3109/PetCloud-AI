from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class InventoryOut(BaseModel):
    product_id: int
    quantity: int
    low_stock_threshold: int
    is_low_stock: bool
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InventoryAdjust(BaseModel):
    delta: int = Field(..., description="Cantidad a sumar (positivo) o restar (negativo) del stock actual")
