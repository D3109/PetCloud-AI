from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None


class UserAdminCreate(UserCreate):
    """Creacion de usuario hecha por un admin/root: permite fijar el rol
    de una vez (dentro de lo que el rol del creador tiene permitido asignar)."""
    role: str = "customer"


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None = None
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
    current_password: str | None = None
    new_password: str | None = None
