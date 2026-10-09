from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    email = decode_access_token(credentials.credentials)
    if email is None:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Esta cuenta esta bloqueada",
        )
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Admin o root: administracion general (usuarios, productos, pedidos)."""
    if current_user.role not in ("admin", "root"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user


def require_root(current_user: User = Depends(get_current_user)) -> User:
    """Solo el superadministrador ROOT."""
    if current_user.role != "root":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Root privileges required",
        )
    return current_user


def require_product_manager(current_user: User = Depends(get_current_user)) -> User:
    """Root, admin o gestor de productos: pueden administrar el catalogo."""
    if current_user.role not in ("root", "admin", "gestor_productos"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Product management privileges required",
        )
    return current_user


def require_support(current_user: User = Depends(get_current_user)) -> User:
    """Root, admin o atencion al cliente: pueden consultar pedidos y encuestas."""
    if current_user.role not in ("root", "admin", "atencion_cliente"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Support privileges required",
        )
    return current_user
