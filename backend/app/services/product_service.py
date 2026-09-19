from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.product import Product
from app.schemas.product import ProductCreate


def create_product(db: Session, data: ProductCreate) -> Product:
    categories = []
    if data.category_ids:
        categories = db.query(Category).filter(
            Category.id.in_(data.category_ids)
        ).all()
        found_ids = {c.id for c in categories}
        missing = set(data.category_ids) - found_ids
        if missing:
            raise ValueError(f"Categories not found: {sorted(missing)}")

    product = Product(
        name=data.name,
        description=data.description,
        price=data.price,
        sku=data.sku,
        is_active=1,
        categories=categories,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def list_products(db: Session, skip: int = 0, limit: int = 100) -> list[Product]:
    return db.query(Product).offset(skip).limit(limit).all()


def get_product(db: Session, product_id: int) -> Product | None:
    return db.query(Product).filter(Product.id == product_id).first()


def get_product_by_sku(db: Session, sku: str) -> Product | None:
    return db.query(Product).filter(Product.sku == sku).first()
