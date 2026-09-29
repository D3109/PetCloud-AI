from sqlalchemy.orm import Session

from app.models.inventory import Inventory


def create_inventory_for_product(db: Session, product_id: int) -> Inventory:
    inventory = Inventory(product_id=product_id, quantity=0)
    db.add(inventory)
    db.commit()
    db.refresh(inventory)
    return inventory


def get_inventory(db: Session, product_id: int) -> Inventory | None:
    return db.query(Inventory).filter(Inventory.product_id == product_id).first()


def adjust_stock(db: Session, product_id: int, delta: int) -> Inventory:
    inventory = get_inventory(db, product_id)
    if inventory is None:
        raise ValueError("Inventory record not found for this product")

    new_quantity = inventory.quantity + delta
    if new_quantity < 0:
        raise ValueError(
            f"Insufficient stock: current is {inventory.quantity}, cannot subtract {abs(delta)}"
        )

    inventory.quantity = new_quantity
    db.commit()
    db.refresh(inventory)
    return inventory


def to_out_dict(inventory: Inventory) -> dict:
    return {
        "product_id": inventory.product_id,
        "quantity": inventory.quantity,
        "low_stock_threshold": inventory.low_stock_threshold,
        "is_low_stock": inventory.quantity <= inventory.low_stock_threshold,
        "updated_at": inventory.updated_at,
    }
