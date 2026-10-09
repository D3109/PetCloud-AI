from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.inventory import Inventory
from app.models.order import Order, OrderItem
from app.services.cart_service import get_or_create_cart
from app.services.promotion_service import get_active_promotion


def checkout(db: Session, user_id: int, promotion_code: str | None = None) -> Order:
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

    discount_percent = Decimal("0")
    applied_code = None
    if promotion_code:
        promotion = get_active_promotion(db, promotion_code)
        if promotion is None:
            raise ValueError(f"Promotion code '{promotion_code}' is not valid or is inactive")
        discount_percent = promotion.discount_percent
        applied_code = promotion.code

    order = Order(user_id=user_id, status="pending", subtotal_amount=0, discount_amount=0, total_amount=0)
    db.add(order)
    db.flush()

    subtotal = Decimal("0")
    for item in cart.items:
        unit_price = item.product.price
        subtotal += unit_price * item.quantity

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

    discount_amount = (subtotal * discount_percent / Decimal("100")).quantize(Decimal("0.01"))
    total = subtotal - discount_amount

    order.subtotal_amount = subtotal
    order.discount_amount = discount_amount
    order.total_amount = total
    order.promotion_code = applied_code

    db.commit()
    db.refresh(order)
    return order


def list_orders(db: Session, user_id: int) -> list[Order]:
    return db.query(Order).filter(Order.user_id == user_id).all()


def get_order(db: Session, user_id: int, order_id: int) -> Order | None:
    return db.query(Order).filter(
        Order.id == order_id, Order.user_id == user_id
    ).first()


def list_all_orders(
    db: Session, skip: int = 0, limit: int = 100, status: str | None = None
) -> list[Order]:
    """Para uso administrativo (admin/root/atencion_cliente): todos los
    pedidos de todos los clientes, opcionalmente filtrados por estado."""
    query = db.query(Order).order_by(Order.created_at.desc())
    if status:
        query = query.filter(Order.status == status)
    return query.offset(skip).limit(limit).all()


def get_any_order(db: Session, order_id: int) -> Order | None:
    """Para uso administrativo: busca un pedido sin restringir por dueño."""
    return db.query(Order).filter(Order.id == order_id).first()


def to_out_dict(order: Order, include_user: bool = False) -> dict:
    data = {
        "id": order.id,
        "status": order.status,
        "subtotal_amount": order.subtotal_amount,
        "discount_amount": order.discount_amount,
        "total_amount": order.total_amount,
        "promotion_code": order.promotion_code,
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
    if include_user:
        data["user_id"] = order.user_id
        data["user_email"] = order.user.email if order.user else None
    return data
