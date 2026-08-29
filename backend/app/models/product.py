from sqlalchemy import Column, Integer, String, Numeric, DateTime, Table, ForeignKey, func
from sqlalchemy.orm import relationship

from app.core.database import Base

product_categories = Table(
    "product_categories",
    Base.metadata,
    Column("product_id", ForeignKey("products.id"), primary_key=True),
    Column("category_id", ForeignKey("categories.id"), primary_key=True),
)


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(String, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    sku = Column(String, unique=True, nullable=False, index=True)
    is_active = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    categories = relationship(
        "Category", secondary=product_categories, back_populates="products"
    )
