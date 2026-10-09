from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.inventory import Inventory
from app.models.order import Order
from app.models.product import Product
from app.models.user import User
from app.services import audit_service, survey_service


def get_dashboard(db: Session) -> dict:
    total_users = db.query(func.count(User.id)).scalar() or 0
    active_users = db.query(func.count(User.id)).filter(User.is_active == 1).scalar() or 0

    products_active = (
        db.query(func.count(Product.id)).filter(Product.is_active == 1).scalar() or 0
    )
    products_inactive = (
        db.query(func.count(Product.id)).filter(Product.is_active == 0).scalar() or 0
    )

    low_stock_count = (
        db.query(func.count(Inventory.id))
        .filter(Inventory.quantity <= Inventory.low_stock_threshold)
        .scalar()
        or 0
    )

    orders_by_status_rows = (
        db.query(Order.status, func.count(Order.id)).group_by(Order.status).all()
    )
    orders_by_status = {status: count for status, count in orders_by_status_rows}

    total_sales = (
        db.query(func.coalesce(func.sum(Order.total_amount), 0))
        .filter(Order.status == "paid")
        .scalar()
        or 0
    )

    survey_stats = survey_service.get_stats(db)
    recent_audit = audit_service.list_audit_logs(db, skip=0, limit=10)
    recent_surveys = survey_service.get_recent(db, limit=5)

    return {
        "total_users": total_users,
        "active_users": active_users,
        "blocked_users": total_users - active_users,
        "products_active": products_active,
        "products_inactive": products_inactive,
        "low_stock_count": low_stock_count,
        "orders_by_status": orders_by_status,
        "total_sales": float(total_sales),
        "survey_total_respuestas": survey_stats.total_respuestas,
        "survey_promedio_satisfaccion": survey_stats.promedio_nivel_satisfaccion,
        "recent_surveys": recent_surveys,
        "recent_audit": recent_audit,
    }
