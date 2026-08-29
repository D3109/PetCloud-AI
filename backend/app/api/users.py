from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.user import UserCreate, UserOut
from app.services import user_service

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.post("", response_model=UserOut, status_code=201)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = user_service.get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    return user_service.create_user(db, user_in)


@router.get("", response_model=list[UserOut])
def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return user_service.list_users(db, skip, limit)


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
