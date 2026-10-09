from pydantic import BaseModel

from app.schemas.audit import AuditLogOut


class DashboardOut(BaseModel):
    total_users: int
    active_users: int
    blocked_users: int
    products_active: int
    products_inactive: int
    low_stock_count: int
    orders_by_status: dict[str, int]
    total_sales: float
    survey_total_respuestas: int
    survey_promedio_satisfaccion: float
    recent_audit: list[AuditLogOut]
