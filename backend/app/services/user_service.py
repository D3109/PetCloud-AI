from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserAdminCreate, UserCreate

VALID_ROLES = {"customer", "admin"}


def create_user(db: Session, user_in: UserCreate) -> User:
    user = User(
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        full_name=user_in.full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_user_as_admin(db: Session, user_in: UserAdminCreate) -> User:
    if user_in.role not in VALID_ROLES:
        raise ValueError(f"Rol invalido: {user_in.role}. Debe ser uno de {sorted(VALID_ROLES)}")
    user = User(
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        full_name=user_in.full_name,
        role=user_in.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def list_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
    return db.query(User).offset(skip).limit(limit).all()


def update_role(db: Session, user: User, role: str) -> User:
    if role not in VALID_ROLES:
        raise ValueError(f"Rol invalido: {role}. Debe ser uno de {sorted(VALID_ROLES)}")
    user.role = role
    db.commit()
    db.refresh(user)
    return user
