from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60
    google_api_key: str
    ai_model: str = "gemini-3.8-flash"
    google_oauth_client_id: str | None = None
    # URL publica del frontend (p. ej. https://xxxx-5500.app.github.dev), usada
    # para armar el enlace clickeable de "restablecer contraseña" en el correo.
    # Si no se configura, el correo igual incluye el token para pegarlo a mano
    # en la pagina de reset-password.
    frontend_base_url: str | None = None
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_from: str | None = None
    smtp_use_tls: bool = True

    model_config = SettingsConfigDict(env_file="../.env")


settings = Settings()
