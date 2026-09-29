from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60
    google_api_key: str
    ai_model: str = "gemini-2.5-flash"

    model_config = SettingsConfigDict(env_file="../.env")


settings = Settings()
