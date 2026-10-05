from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.payment import Payment


def pay_order(db: Session, user_id: int, order_id: int, method: str = "simulated") -> Payment:
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == user_id).first()
    if order is None:
        raise ValueError("Order not found")
    if order.status == "paid":
        raise ValueError("Order is already paid")

    existing = db.query(Payment).filter(Payment.order_id == order_id).first()
    if existing:
        raise ValueError("A payment already exists for this order")

    payment = Payment(
        order_id=order_id,
        amount=order.total_amount,
        method=method,
        status="completed",
    )
    db.add(payment)

    order.status = "paid"

    db.commit()
    db.refresh(payment)
    return payment
