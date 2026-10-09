from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.security import create_access_token, verify_password
from app.models.user import User
from app.schemas.auth import GoogleLoginRequest, LoginRequest, TokenResponse
from app.schemas.user import UserOut
from app.services.google_auth_service import (
    GoogleLoginNotConfigured,
    InvalidGoogleToken,
    find_or_create_user_from_google,
    verify_google_id_token,
)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Esta cuenta esta bloqueada")

    token = create_access_token(subject=user.email)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserOut)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/google", response_model=TokenResponse)
def login_with_google(payload: GoogleLoginRequest, db: Session = Depends(get_db)):
    try:
        google_payload = verify_google_id_token(payload.id_token)
    except GoogleLoginNotConfigured as exc:
        raise HTTPException(status_code=501, detail=str(exc))
    except InvalidGoogleToken as exc:
        raise HTTPException(status_code=401, detail=str(exc))

    user = find_or_create_user_from_google(db, google_payload)
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Esta cuenta esta bloqueada")

    token = create_access_token(subject=user.email)
    return TokenResponse(access_token=token)
