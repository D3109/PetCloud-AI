from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.pet import PetCreate, PetOut
from app.services import pet_service

router = APIRouter(prefix="/api/v1/pets", tags=["pets"])


@router.post("", response_model=PetOut, status_code=201)
def create_pet(
    pet_in: PetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return pet_service.create_pet(db, current_user, pet_in)


@router.get("", response_model=list[PetOut])
def list_my_pets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return pet_service.list_pets_for_user(db, current_user)
