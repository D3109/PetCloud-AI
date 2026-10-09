from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_product_manager
from app.models.user import User
from app.schemas.product import ProductCreate, ProductOut, ProductUpdate
from app.services import audit_service, product_service

router = APIRouter(prefix="/api/v1/products", tags=["products"])


@router.post("", response_model=ProductOut, status_code=201)
def create_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_product_manager),
):
    existing = product_service.get_product_by_sku(db, data.sku)
    if existing:
        raise HTTPException(status_code=400, detail="SKU already exists")
    try:
        product = product_service.create_product(db, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    audit_service.log_action(
        db, current_user, "create_product", "product", product.id, product.sku
    )
    return product


@router.get("", response_model=list[ProductOut])
def list_products(
    skip: int = 0,
    limit: int = 100,
    include_inactive: bool = False,
    db: Session = Depends(get_db),
):
    return product_service.list_products(db, skip, limit, include_inactive)


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = product_service.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_product_manager),
):
    product = product_service.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    try:
        product = product_service.update_product(db, product, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    audit_service.log_action(
        db, current_user, "update_product", "product", product.id, product.sku
    )
    return product


@router.delete("/{product_id}", status_code=204)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_product_manager),
):
    product = product_service.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product_service.deactivate_product(db, product)
    audit_service.log_action(
        db, current_user, "deactivate_product", "product", product.id, product.sku
    )
