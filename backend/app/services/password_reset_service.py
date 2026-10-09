"""Logica de recuperacion de contraseña por correo.

Flujo:
1. El usuario pide un reset con su correo (forgot-password).
2. Se genera un token aleatorio largo (secrets.token_urlsafe), se guarda en
   la base de datos SOLO su hash SHA-256 (igual que una contraseña, para
   que una fuga de la base de datos no sirva para restablecer cuentas), y
   el token en texto plano se manda por correo.
3. El usuario entra al enlace del correo, que trae el token, y envia su
   nueva contraseña (reset-password). Se valida que el token exista, no
   haya expirado y no se haya usado ya; si es valido se cambia la
   contraseña y se marca el token como usado (un solo uso).

Por diseño, forgot-password SIEMPRE responde el mismo mensaje exista o no
el correo en el sistema, para no permitir que alguien use este endpoint
para averiguar que correos estan registrados (enumeracion de usuarios).
"""
import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.password_reset_token import PasswordResetToken
from app.models.user import User

TOKEN_TTL_MINUTES = 30


def _hash_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def create_reset_token(db: Session, user: User) -> str:
    """Crea un token de reset para `user` y devuelve el token en texto
    plano (para incluirlo en el correo). Invalida cualquier token anterior
    sin usar de ese usuario, para que solo el enlace mas reciente funcione.
    """
    now = datetime.now(timezone.utc)
    db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user.id,
        PasswordResetToken.used_at.is_(None),
    ).delete()

    raw_token = secrets.token_urlsafe(32)
    entry = PasswordResetToken(
        user_id=user.id,
        token_hash=_hash_token(raw_token),
        expires_at=now + timedelta(minutes=TOKEN_TTL_MINUTES),
    )
    db.add(entry)
    db.commit()
    return raw_token


def reset_password(db: Session, raw_token: str, new_password: str) -> bool:
    """Valida el token y, si es valido, cambia la contraseña del usuario
    asociado. Devuelve True si se realizo el cambio, False si el token no
    existe, ya expiro o ya fue usado."""
    now = datetime.now(timezone.utc)
    token_hash = _hash_token(raw_token)
    entry = (
        db.query(PasswordResetToken)
        .filter(PasswordResetToken.token_hash == token_hash)
        .first()
    )
    if entry is None or entry.used_at is not None:
        return False

    expires_at = entry.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < now:
        return False

    user = db.query(User).filter(User.id == entry.user_id).first()
    if user is None:
        return False

    user.hashed_password = hash_password(new_password)
    entry.used_at = now
    db.commit()
    return True
