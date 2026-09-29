from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_admin
from app.models.user import User
from app.schemas.inventory import InventoryAdjust, InventoryOut
from app.services import inventory_service

router = APIRouter(prefix="/api/v1/inventory", tags=["inventory"])


@router.get("/{product_id}", response_model=InventoryOut)
def get_inventory(product_id: int, db: Session = Depends(get_db)):
    inventory = inventory_service.get_inventory(db, product_id)
    if inventory is None:
        raise HTTPException(status_code=404, detail="Inventory not found for this product")
    return inventory_service.to_out_dict(inventory)


@router.put("/{product_id}/adjust", response_model=InventoryOut)
def adjust_inventory(
    product_id: int,
    data: InventoryAdjust,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    try:
        inventory = inventory_service.adjust_stock(db, product_id, data.delta)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return inventory_service.to_out_dict(inventory)
