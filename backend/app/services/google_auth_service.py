"""Verificacion de tokens de Google Sign-In y logica de
buscar/vincular/crear el usuario correspondiente en nuestra base de datos.

Diseno: si GOOGLE_OAUTH_CLIENT_ID no esta configurado en el entorno, la
funcion de verificacion lanza GoogleLoginNotConfigured, que el endpoint
convierte en un 501 claro ("Google login no configurado") en vez de fallar
de forma confusa.
"""
import secrets

from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password
from app.models.user import User


class GoogleLoginNotConfigured(Exception):
    """GOOGLE_OAUTH_CLIENT_ID no esta configurado en el backend."""


class InvalidGoogleToken(Exception):
    """El id_token de Google no pudo ser verificado."""


def verify_google_id_token(raw_id_token: str) -> dict:
    if not settings.google_oauth_client_id:
        raise GoogleLoginNotConfigured(
            "El login con Google no esta configurado en el servidor "
            "(falta GOOGLE_OAUTH_CLIENT_ID)."
        )
    try:
        payload = google_id_token.verify_oauth2_token(
            raw_id_token,
            google_requests.Request(),
            settings.google_oauth_client_id,
        )
    except Exception as exc:  # google-auth lanza varias excepciones propias
        raise InvalidGoogleToken(f"Token de Google invalido: {exc}") from exc

    if payload.get("iss") not in ("accounts.google.com", "https://accounts.google.com"):
        raise InvalidGoogleToken("Emisor del token invalido")

    return payload


def find_or_create_user_from_google(db: Session, payload: dict) -> User:
    google_sub = payload["sub"]
    email = payload.get("email")
    full_name = payload.get("name")

    if not email:
        raise InvalidGoogleToken("El token de Google no incluye un correo")

    user = db.query(User).filter(User.google_sub == google_sub).first()
    if user:
        return user

    user = db.query(User).filter(User.email == email).first()
    if user:
        # Cuenta local existente con el mismo correo: la vinculamos con Google.
        user.google_sub = google_sub
        if user.auth_provider == "local" and not user.full_name and full_name:
            user.full_name = full_name
        db.commit()
        db.refresh(user)
        return user

    # Usuario nuevo originado en Google: contrasena local inutilizable
    # (nadie puede iniciar sesion local con ella porque nadie la conoce).
    random_password = secrets.token_urlsafe(32)
    user = User(
        email=email,
        hashed_password=hash_password(random_password),
        full_name=full_name,
        role="customer",
        is_active=1,
        auth_provider="google",
        google_sub=google_sub,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
