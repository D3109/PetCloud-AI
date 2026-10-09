from sqlalchemy.orm import Session

from app.models.pet import Pet
from app.models.user import User
from app.schemas.pet import PetCreate


def create_pet(db: Session, user: User, pet_in: PetCreate) -> Pet:
    pet = Pet(
        user_id=user.id,
        name=pet_in.name,
        species=pet_in.species,
        breed=pet_in.breed,
        birth_date=pet_in.birth_date,
    )
    db.add(pet)
    db.commit()
    db.refresh(pet)
    return pet


def list_pets_for_user(db: Session, user: User) -> list[Pet]:
    return (
        db.query(Pet)
        .filter(Pet.user_id == user.id)
        .order_by(Pet.created_at.desc())
        .all()
    )
