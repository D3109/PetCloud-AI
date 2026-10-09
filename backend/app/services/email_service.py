"""Envio de correos de alerta (confirmacion de pedido pagado).

Disenado para degradar con elegancia: si no hay credenciales SMTP
configuradas (SMTP_HOST/SMTP_USER/SMTP_PASSWORD/SMTP_FROM en el .env), la
funcion simplemente registra el intento en el log y no falla ni bloquea
el flujo de pago. Asi el pago siempre se completa aunque el correo no se
pueda enviar todavia.
"""
import logging
import smtplib
from email.message import EmailMessage

from app.core.config import settings

logger = logging.getLogger("petcloud.email")


def is_email_configured() -> bool:
    return bool(
        settings.smtp_host and settings.smtp_user and settings.smtp_password and settings.smtp_from
    )


def _send_email(to_email: str, subject: str, body: str) -> bool:
    if not is_email_configured():
        logger.info(
            "SMTP no configurado: se omite el envio de correo a %s (asunto: %s)",
            to_email,
            subject,
        )
        return False

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = settings.smtp_from
    message["To"] = to_email
    message.set_content(body)

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as server:
            if settings.smtp_use_tls:
                server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(message)
        logger.info("Correo enviado a %s (asunto: %s)", to_email, subject)
        return True
    except Exception:
        logger.exception("Fallo al enviar correo a %s", to_email)
        return False


def send_order_paid_email(to_email: str, order) -> bool:
    """Notifica al cliente que su pedido fue pagado exitosamente.

    `order` es el modelo Order ya actualizado a status="paid", con sus
    items y relaciones cargadas.
    """
    lines = [
        f"Hola,",
        "",
        f"Tu pedido #{order.id} en PetCloud fue pagado exitosamente.",
        "",
        "Resumen del pedido:",
    ]
    for item in order.items:
        nombre = item.product.name if item.product else f"Producto #{item.product_id}"
        lines.append(f"  - {nombre} x{item.quantity}: ${item.unit_price * item.quantity}")

    lines += [
        "",
        f"Subtotal: ${order.subtotal_amount}",
        f"Descuento: ${order.discount_amount}",
        f"Total: ${order.total_amount}",
        "",
        "Gracias por tu compra en PetCloud.",
    ]
    body = "\n".join(lines)
    return _send_email(to_email, f"PetCloud - Confirmacion de pedido #{order.id}", body)


def send_password_reset_email(to_email: str, reset_url: str) -> bool:
    """Envia el enlace para restablecer la contraseña. El enlace ya incluye
    el token; expira a los 30 minutos (ver password_reset_service)."""
    lines = [
        "Hola,",
        "",
        "Recibimos una solicitud para restablecer la contraseña de tu cuenta en PetCloud.",
        "Si fuiste tu, usa este enlace (valido por 30 minutos):",
        "",
        reset_url,
        "",
        "Si no solicitaste esto, puedes ignorar este correo: tu contraseña no cambiara.",
    ]
    body = "\n".join(lines)
    return _send_email(to_email, "PetCloud - Restablecer contraseña", body)


def send_order_paid_admin_alert(admin_emails: list[str], order, customer_email: str | None) -> bool:
    """Notifica al equipo de soporte/admin que hay un nuevo pedido pagado."""
    if not admin_emails:
        return False

    lines = [
        f"Nuevo pedido pagado: #{order.id}",
        f"Cliente: {customer_email or 'desconocido'}",
        f"Total: ${order.total_amount}",
        f"Cantidad de items: {len(order.items)}",
    ]
    body = "\n".join(lines)

    sent_any = False
    for email in admin_emails:
        if _send_email(email, f"PetCloud - Nuevo pedido pagado #{order.id}", body):
            sent_any = True
    return sent_any
