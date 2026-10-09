from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.user import ProfileUpdate, UserAdminCreate, UserCreate
from app.services import pet_service

# Roles que existen en el sistema. "root" NO se incluye en los roles
# asignables por API (ni por admin ni por root): el usuario ROOT solo se
# crea o promueve directamente en la base de datos mediante
# scripts/create_root.py, nunca a traves de un endpoint HTTP.
ALL_ROLES = {"customer", "atencion_cliente", "gestor_productos", "admin", "root"}
API_ASSIGNABLE_ROLES = {"customer", "atencion_cliente", "gestor_productos", "admin"}

# Lo que un admin "normal" (no root) puede asignar al crear o cambiar el rol
# de otro usuario. Un admin no puede crear ni ascender a otro admin: eso
# evita que administradores ordinarios se repartan privilegios entre ellos.
ADMIN_ASSIGNABLE_ROLES = {"customer", "atencion_cliente", "gestor_productos"}

VALID_ROLES = API_ASSIGNABLE_ROLES  # compatibilidad con código existente


def roles_assignable_by(actor_role: str) -> set[str]:
    if actor_role == "root":
        return API_ASSIGNABLE_ROLES
    if actor_role == "admin":
        return ADMIN_ASSIGNABLE_ROLES
    return set()


def create_user(db: Session, user_in: UserCreate) -> User:
    user = User(
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        full_name=user_in.full_name,
        phone=user_in.phone,
        address=user_in.address,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    if user_in.pet is not None:
        pet_service.create_pet(db, user, user_in.pet)

    return user


def create_user_as_admin(db: Session, user_in: UserAdminCreate, actor: User) -> User:
    if user_in.role not in API_ASSIGNABLE_ROLES:
        raise ValueError(f"Rol invalido: {user_in.role}. Debe ser uno de {sorted(API_ASSIGNABLE_ROLES)}")
    if user_in.role not in roles_assignable_by(actor.role):
        raise ValueError(
            f"No tienes permiso para crear un usuario con el rol '{user_in.role}'"
        )
    user = User(
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        full_name=user_in.full_name,
        phone=user_in.phone,
        address=user_in.address,
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


def update_role(db: Session, user: User, role: str, actor: User) -> User:
    if user.role == "root":
        raise ValueError("El usuario ROOT no puede ser modificado desde aqui")
    if role not in API_ASSIGNABLE_ROLES:
        raise ValueError(f"Rol invalido: {role}. Debe ser uno de {sorted(API_ASSIGNABLE_ROLES)}")
    if role not in roles_assignable_by(actor.role):
        raise ValueError(f"No tienes permiso para asignar el rol '{role}'")
    user.role = role
    db.commit()
    db.refresh(user)
    return user


def update_own_profile(db: Session, user: User, data: ProfileUpdate) -> User:
    """Permite a un usuario modificar su propio nombre y/o contraseña.

    No permite cambiar email ni rol desde aqui (eso evita que alguien se
    auto-asigne privilegios por esta via). Los usuarios originados en
    Google (auth_provider="google") no tienen una contraseña que el
    usuario conozca, asi que no pueden cambiarla por este endpoint.
    """
    if data.full_name is not None:
        user.full_name = data.full_name
    if data.phone is not None:
        user.phone = data.phone
    if data.address is not None:
        user.address = data.address

    if data.new_password:
        if user.auth_provider == "google":
            raise ValueError(
                "Esta cuenta inicia sesion con Google y no tiene contraseña local"
            )
        if not data.current_password or not verify_password(
            data.current_password, user.hashed_password
        ):
            raise ValueError("La contraseña actual no es correcta")
        user.hashed_password = hash_password(data.new_password)

    db.commit()
    db.refresh(user)
    return user


def set_active(db: Session, user: User, is_active: bool, actor: User) -> User:
    if user.role == "root":
        raise ValueError("El usuario ROOT no puede ser bloqueado")
    if user.id == actor.id:
        raise ValueError("No puedes bloquear tu propia cuenta")
    user.is_active = 1 if is_active else 0
    db.commit()
    db.refresh(user)
    return user
