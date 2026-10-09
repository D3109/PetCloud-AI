from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core import rate_limit
from app.core.config import settings
from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.security import create_access_token, verify_password
from app.models.user import User
from app.schemas.auth import (
    ForgotPasswordRequest,
    GoogleLoginRequest,
    LoginRequest,
    MessageResponse,
    ResetPasswordRequest,
    TokenResponse,
)
from app.schemas.user import ProfileUpdate, UserOut
from app.services import password_reset_service, user_service
from app.services.email_service import send_password_reset_email
from app.services.google_auth_service import (
    GoogleLoginNotConfigured,
    InvalidGoogleToken,
    find_or_create_user_from_google,
    verify_google_id_token,
)

GENERIC_RESET_MESSAGE = (
    "Si el correo esta registrado, te enviamos un enlace para restablecer "
    "tu contraseña. Revisa tu bandeja de entrada (y spam)."
)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    email_key = credentials.email.lower()

    if rate_limit.is_locked(email_key):
        raise HTTPException(
            status_code=429,
            detail="Demasiados intentos fallidos. Intenta de nuevo en unos minutos.",
        )

    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        rate_limit.register_failure(email_key)
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Esta cuenta esta bloqueada")

    rate_limit.clear(email_key)
    token = create_access_token(subject=user.email)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserOut)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserOut)
def update_current_user_profile(
    data: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return user_service.update_own_profile(db, current_user, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/forgot-password", response_model=MessageResponse)
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    email_key = payload.email.lower()

    # Mismo mensaje siempre, exista o no el correo, y aunque este limitado
    # por frecuencia: asi este endpoint nunca revela si un correo esta
    # registrado en el sistema.
    if rate_limit.is_reset_rate_limited(email_key):
        return MessageResponse(message=GENERIC_RESET_MESSAGE)

    user = db.query(User).filter(User.email == payload.email).first()
    if user is not None and user.is_active and user.auth_provider == "local":
        rate_limit.register_reset_request(email_key)
        raw_token = password_reset_service.create_reset_token(db, user)
        if settings.frontend_base_url:
            reset_url = f"{settings.frontend_base_url.rstrip('/')}/reset-password.html?token={raw_token}"
        else:
            reset_url = (
                "Abre reset-password.html en el sitio de PetCloud y pega este "
                f"codigo cuando te lo pida: {raw_token}"
            )
        send_password_reset_email(user.email, reset_url)

    return MessageResponse(message=GENERIC_RESET_MESSAGE)


@router.post("/reset-password", response_model=MessageResponse)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    ok = password_reset_service.reset_password(db, payload.token, payload.new_password)
    if not ok:
        raise HTTPException(
            status_code=400,
            detail="El enlace no es valido o ya expiro. Solicita uno nuevo.",
        )
    return MessageResponse(message="Tu contraseña fue actualizada. Ya puedes iniciar sesion.")


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
