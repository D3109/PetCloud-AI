from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_admin
from app.models.user import User
from app.schemas.product import ProductCreate, ProductOut
from app.services import product_service

router = APIRouter(prefix="/api/v1/products", tags=["products"])


@router.post("", response_model=ProductOut, status_code=201)
def create_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    existing = product_service.get_product_by_sku(db, data.sku)
    if existing:
        raise HTTPException(status_code=400, detail="SKU already exists")
    try:
        return product_service.create_product(db, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=list[ProductOut])
def list_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return product_service.list_products(db, skip, limit)


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = product_service.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
