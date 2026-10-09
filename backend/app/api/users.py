from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_admin
from app.models.user import User
from app.schemas.user import UserActiveUpdate, UserAdminCreate, UserCreate, UserOut, UserRoleUpdate
from app.services import audit_service, user_service

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.post("", response_model=UserOut, status_code=201)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = user_service.get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    return user_service.create_user(db, user_in)


@router.post("/admin", response_model=UserOut, status_code=201)
def create_user_as_admin(
    user_in: UserAdminCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Crea un usuario directamente desde el panel admin (sin autoregistro),
    pudiendo fijar su rol desde el inicio (dentro de lo que el rol del
    creador tiene permitido asignar)."""
    existing = user_service.get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    try:
        user = user_service.create_user_as_admin(db, user_in, current_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    audit_service.log_action(
        db, current_user, "create_user", "user", user.id, f"role={user.role}"
    )
    return user


@router.get("", response_model=list[UserOut])
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return user_service.list_users(db, skip, limit)


@router.get("/{user_id}", response_model=UserOut)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    user = user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/{user_id}/role", response_model=UserOut)
def update_user_role(
    user_id: int,
    data: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    if user_id == current_user.id:
        raise HTTPException(
            status_code=400, detail="No puedes cambiar tu propio rol"
        )
    user = user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    previous_role = user.role
    try:
        user = user_service.update_role(db, user, data.role, current_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    audit_service.log_action(
        db, current_user, "update_role", "user", user.id,
        f"{previous_role} -> {user.role}",
    )
    return user


@router.patch("/{user_id}/active", response_model=UserOut)
def update_user_active(
    user_id: int,
    data: UserActiveUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    user = user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    try:
        user = user_service.set_active(db, user, data.is_active, current_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    audit_service.log_action(
        db, current_user, "set_active", "user", user.id,
        f"is_active={bool(data.is_active)}",
    )
    return user
