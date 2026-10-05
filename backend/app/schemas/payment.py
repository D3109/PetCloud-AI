from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class PaymentCreate(BaseModel):
    method: str = "simulated"


class PaymentOut(BaseModel):
    id: int
    order_id: int
    amount: Decimal
    method: str
    status: str
    paid_at: datetime

    model_config = ConfigDict(from_attributes=True)
