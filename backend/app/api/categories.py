from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_admin
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryOut
from app.services import category_service

router = APIRouter(prefix="/api/v1/categories", tags=["categories"])


@router.post("", response_model=CategoryOut, status_code=201)
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return category_service.create_category(db, data)


@router.get("", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return category_service.list_categories(db)


@router.get("/{category_id}", response_model=CategoryOut)
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = category_service.get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category
