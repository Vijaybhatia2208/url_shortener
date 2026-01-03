from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.config import get_settings

settings = get_settings()

# SQLite requires connect_args for multi-thread access
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}  # needed for SQLite only
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


def get_db():
    """FastAPI dependency — yields a DB session per request, auto-closes after."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
