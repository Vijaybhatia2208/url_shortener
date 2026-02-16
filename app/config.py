from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env file."""

    DATABASE_URL: str = "sqlite:///./url_shortener.db"
    BASE_URL: str = "http://localhost:8000"
    SHORT_CODE_LENGTH: int = 6

    # Google OAuth2
    GOOGLE_CLIENT_ID: str = ""

    # JWT
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440  # 24 hours

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance — reads .env only once."""
    return Settings()
