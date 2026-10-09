from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, field_validator

ESPECIES_VALIDAS = {"perro", "gato", "otro"}


class PetCreate(BaseModel):
    name: str
    species: str
    breed: str | None = None
    birth_date: date | None = None

    @field_validator("species")
    @classmethod
    def species_must_be_valid(cls, v: str) -> str:
        v = v.strip().lower()
        if v not in ESPECIES_VALIDAS:
            raise ValueError("species debe ser 'perro', 'gato' u 'otro'")
        return v

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("El nombre de la mascota no puede estar vacío")
        return v


class PetOut(BaseModel):
    id: int
    user_id: int
    name: str
    species: str
    breed: str | None = None
    birth_date: date | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
