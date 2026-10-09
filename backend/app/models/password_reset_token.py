from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class PasswordResetToken(Base):
    """Token de un solo uso para restablecer la contraseña.

    Se guarda un hash SHA-256 del token (nunca el token en texto plano),
    igual que se hace con las contraseñas, para que una fuga de la base de
    datos no permita restablecer contraseñas de cuentas ajenas. El token
    real se envia solo por correo al usuario que lo solicito.
    """

    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    token_hash = Column(String, unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")
