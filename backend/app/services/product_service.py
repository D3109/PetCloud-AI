from decimal import Decimal

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from app.services import inventory_service


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
        image_url=data.image_url,
        brand=data.brand,
        pet_type=data.pet_type,
        is_active=1,
        categories=categories,
    )
    db.add(product)
    db.commit()
    db.refresh(product)

    inventory_service.create_inventory_for_product(db, product.id)

    return product


def list_products(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    include_inactive: bool = False,
    q: str | None = None,
    category_id: int | None = None,
    pet_type: str | None = None,
    min_price: Decimal | None = None,
    max_price: Decimal | None = None,
) -> list[Product]:
    """Lista productos con busqueda y filtros opcionales:
    - q: busca coincidencias (sin importar mayusculas) en nombre, marca y
      descripcion, para que "correa" encuentre tambien productos cuya
      marca o descripcion mencionen la palabra.
    - category_id, pet_type: filtran por categoria exacta y tipo de mascota.
    - min_price/max_price: rango de precio (cualquiera de los dos es opcional).
    """
    query = db.query(Product)
    if not include_inactive:
        query = query.filter(Product.is_active == 1)

    if q:
        like = f"%{q.strip()}%"
        query = query.filter(
            or_(
                Product.name.ilike(like),
                Product.brand.ilike(like),
                Product.description.ilike(like),
            )
        )

    if category_id is not None:
        query = query.filter(Product.categories.any(Category.id == category_id))

    if pet_type is not None:
        query = query.filter(Product.pet_type == pet_type)

    if min_price is not None:
        query = query.filter(Product.price >= min_price)

    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    return query.offset(skip).limit(limit).all()


def get_product(db: Session, product_id: int) -> Product | None:
    return db.query(Product).filter(Product.id == product_id).first()


def get_product_by_sku(db: Session, sku: str) -> Product | None:
    return db.query(Product).filter(Product.sku == sku).first()


def update_product(db: Session, product: Product, data: ProductUpdate) -> Product:
    if data.name is not None:
        product.name = data.name
    if data.description is not None:
        product.description = data.description
    if data.price is not None:
        product.price = data.price
    if data.image_url is not None:
        product.image_url = data.image_url
    if data.brand is not None:
        product.brand = data.brand
    if data.pet_type is not None:
        product.pet_type = data.pet_type
    if data.is_active is not None:
        product.is_active = data.is_active
    if data.category_ids is not None:
        categories = db.query(Category).filter(
            Category.id.in_(data.category_ids)
        ).all()
        found_ids = {c.id for c in categories}
        missing = set(data.category_ids) - found_ids
        if missing:
            raise ValueError(f"Categories not found: {sorted(missing)}")
        product.categories = categories

    db.commit()
    db.refresh(product)
    return product


def deactivate_product(db: Session, product: Product) -> Product:
    """Baja logica: no se elimina para no romper pedidos historicos."""
    product.is_active = 0
    db.commit()
    db.refresh(product)
    return product
