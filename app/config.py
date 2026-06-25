"""
Application configuration.

All settings are loaded from environment variables (see .env.example at the
repository root). Nothing sensitive is hard-coded here.
"""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # General
    ENV: str = "development"
    APP_NAME: str = "Football Streaming Platform API"
    API_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str = "postgresql+psycopg2://football:football@localhost:5432/football_db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT / Auth
    JWT_SECRET_KEY: str = "change-this-secret-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 12  # 12 hours

    # Telegram
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_BROADCAST_CHAT_ID: str = ""  # optional public channel/group for broadcasts

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173"

    # Rate limiting
    RATE_LIMIT_DEFAULT: str = "100/minute"
    RATE_LIMIT_LOGIN: str = "10/minute"

    # Uploads
    UPLOAD_DIR: str = "app/static/uploads"
    MAX_UPLOAD_SIZE_MB: int = 10

    # First super admin (created automatically on first boot if no admins exist)
    FIRST_SUPER_ADMIN_USERNAME: str = "admin"
    FIRST_SUPER_ADMIN_PASSWORD: str = "ChangeMe123!"
    FIRST_SUPER_ADMIN_EMAIL: str = "admin@example.com"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
