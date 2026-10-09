from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict, field_validator

from app.schemas.pet import PetCreate


def _validate_password_strength(password: str) -> str:
    if len(password) < 8:
        raise ValueError("La contraseña debe tener al menos 8 caracteres")
    if not any(c.isalpha() for c in password):
        raise ValueError("La contraseña debe incluir al menos una letra")
    if not any(c.isdigit() for c in password):
        raise ValueError("La contraseña debe incluir al menos un número")
    return password


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None
    phone: str | None = None
    address: str | None = None
    # Datos basicos de la mascota, capturados opcionalmente durante el
    # registro si el usuario marca que quiere agregarlos.
    pet: PetCreate | None = None

    @field_validator("password")
    @classmethod
    def password_must_be_strong(cls, v: str) -> str:
        return _validate_password_strength(v)


class UserAdminCreate(UserCreate):
    """Creacion de usuario hecha por un admin/root: permite fijar el rol
    de una vez (dentro de lo que el rol del creador tiene permitido asignar)."""
    role: str = "customer"


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None = None
    phone: str | None = None
    address: str | None = None
    role: str
    is_active: int
    auth_provider: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserRoleUpdate(BaseModel):
    role: str


class UserActiveUpdate(BaseModel):
    is_active: bool


class ProfileUpdate(BaseModel):
    """Datos que un usuario puede modificar de su propio perfil."""
    full_name: str | None = None
    phone: str | None = None
    address: str | None = None
    current_password: str | None = None
    new_password: str | None = None

    @field_validator("new_password")
    @classmethod
    def new_password_must_be_strong(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return _validate_password_strength(v)
