"""Exportacion de reportes en CSV para el panel de administrador.

Reutiliza las consultas ya existentes en order_service/survey_service e
inventory_service en vez de duplicar logica de negocio: este router solo
se encarga de darle formato CSV a esos mismos datos.
"""
import csv
import io

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_product_manager, require_support
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.user import User
from app.services import order_service, survey_service

router = APIRouter(prefix="/api/v1/admin/reports", tags=["reports"])


def _csv_response(rows: list[list], header: list[str], filename: str) -> StreamingResponse:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(header)
    writer.writerows(rows)
    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/orders.csv")
def export_orders_csv(
    status: str | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(require_support),
):
    orders = order_service.list_all_orders(db, skip=0, limit=100000, status=status)
    rows = []
    for order in orders:
        rows.append([
            order.id,
            order.user.email if order.user else "",
            order.status,
            str(order.subtotal_amount),
            str(order.discount_amount),
            str(order.total_amount),
            order.created_at.isoformat() if order.created_at else "",
            len(order.items),
        ])
    header = ["ID", "Cliente", "Estado", "Subtotal", "Descuento", "Total", "Fecha", "Articulos"]
    return _csv_response(rows, header, "pedidos.csv")


@router.get("/surveys.csv")
def export_surveys_csv(
    db: Session = Depends(get_db),
    _: User = Depends(require_support),
):
    surveys = survey_service.list_surveys(db, skip=0, limit=100000)
    rows = []
    for s in surveys:
        rows.append([
            s.id,
            s.user.email if s.user else "",
            s.precision_recomendacion,
            s.facilidad_uso,
            s.confianza_usuario,
            s.nivel_satisfaccion,
            s.percepcion_seguridad,
            s.intencion_recompra,
            s.calidad_productos,
            s.atencion_recibida,
            s.facilidad_proceso_compra,
            s.tiempo_entrega,
            (s.comentario or "").replace("\n", " "),
            s.created_at.isoformat() if s.created_at else "",
        ])
    header = [
        "ID", "Usuario", "Precision", "Facilidad", "Confianza", "Satisfaccion",
        "Seguridad", "Recompra", "Calidad productos", "Atencion recibida",
        "Facilidad proceso compra", "Tiempo entrega", "Comentario", "Fecha",
    ]
    return _csv_response(rows, header, "encuestas.csv")


@router.get("/inventory.csv")
def export_inventory_csv(
    db: Session = Depends(get_db),
    _: User = Depends(require_product_manager),
):
    rows_data = (
        db.query(Product, Inventory)
        .outerjoin(Inventory, Inventory.product_id == Product.id)
        .order_by(Product.name)
        .all()
    )
    rows = []
    for product, inventory in rows_data:
        quantity = inventory.quantity if inventory else 0
        threshold = inventory.low_stock_threshold if inventory else 0
        rows.append([
            product.id,
            product.name,
            product.sku,
            product.brand or "",
            quantity,
            threshold,
            "Si" if quantity <= threshold else "No",
            "Activo" if product.is_active else "Inactivo",
        ])
    header = ["ID", "Nombre", "SKU", "Marca", "Existencias", "Umbral minimo", "Stock bajo", "Estado"]
    return _csv_response(rows, header, "inventario.csv")
