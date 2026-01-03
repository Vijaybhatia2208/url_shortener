from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base


def get_utcnow():
    return datetime.now(timezone.utc)


class URL(Base):
    """SQLAlchemy model for shortened URLs."""
    
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True)
    short_code = Column(String, unique=True, index=True, nullable=False)
    original_url = Column(String, nullable=False)
    clicks = Column(Integer, default=0)
    created_at = Column(DateTime, default=get_utcnow)
