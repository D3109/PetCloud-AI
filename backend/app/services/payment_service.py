import logging

from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.payment import Payment
from app.models.user import User
from app.services.email_service import send_order_paid_admin_alert, send_order_paid_email

logger = logging.getLogger("petcloud.payments")


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
    db.refresh(order)

    _notify_order_paid(db, order)

    return payment


def _notify_order_paid(db: Session, order: Order) -> None:
    """Envia alertas por correo (cliente + admins) de forma best-effort.

    Cualquier error aqui queda solo registrado en el log: nunca debe
    hacer fallar un pago que ya se completo correctamente.
    """
    try:
        if order.user and order.user.email:
            send_order_paid_email(order.user.email, order)

        admin_emails = [
            u.email
            for u in db.query(User)
            .filter(User.role.in_(["admin", "root", "atencion_cliente"]))
            .all()
            if u.email
        ]
        send_order_paid_admin_alert(
            admin_emails, order, order.user.email if order.user else None
        )
    except Exception:
        logger.exception("Error enviando notificaciones de pedido pagado #%s", order.id)
