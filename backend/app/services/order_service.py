from sqlalchemy.orm import Session

from app.models.cart import Cart
from app.models.inventory import Inventory
from app.models.order import Order, OrderItem
from app.services.cart_service import get_or_create_cart


def checkout(db: Session, user_id: int) -> Order:
    cart = get_or_create_cart(db, user_id)

    if not cart.items:
        raise ValueError("Cart is empty")

    for item in cart.items:
        inventory = db.query(Inventory).filter(
            Inventory.product_id == item.product_id
        ).first()
        if inventory is None or inventory.quantity < item.quantity:
            available = inventory.quantity if inventory else 0
            raise ValueError(
                f"Insufficient stock for '{item.product.name}': "
                f"requested {item.quantity}, available {available}"
            )

    order = Order(user_id=user_id, status="pending", total_amount=0)
    db.add(order)
    db.flush()

    total = 0
    for item in cart.items:
        unit_price = item.product.price
        total += unit_price * item.quantity

        db.add(OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=unit_price,
        ))

        inventory = db.query(Inventory).filter(
            Inventory.product_id == item.product_id
        ).first()
        inventory.quantity -= item.quantity

        db.delete(item)

    order.total_amount = total
    db.commit()
    db.refresh(order)
    return order


def list_orders(db: Session, user_id: int) -> list[Order]:
    return db.query(Order).filter(Order.user_id == user_id).all()


def get_order(db: Session, user_id: int, order_id: int) -> Order | None:
    return db.query(Order).filter(
        Order.id == order_id, Order.user_id == user_id
    ).first()


def to_out_dict(order: Order) -> dict:
    return {
        "id": order.id,
        "status": order.status,
        "total_amount": order.total_amount,
        "created_at": order.created_at,
        "items": [
            {
                "product_id": item.product_id,
                "product_name": item.product.name,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
            }
            for item in order.items
        ],
    }
