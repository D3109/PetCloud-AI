from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), unique=True, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    method = Column(String, nullable=False, default="simulated")
    status = Column(String, nullable=False, default="completed")
    paid_at = Column(DateTime(timezone=True), server_default=func.now())

    order = relationship("Order")
