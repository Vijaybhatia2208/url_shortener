from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env file."""

    DATABASE_URL: str = "sqlite:///./url_shortener.db"
    BASE_URL: str = "http://localhost:8000"
    SHORT_CODE_LENGTH: int = 6

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance — reads .env only once."""
    return Settings()
