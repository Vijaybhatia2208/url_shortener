from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
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
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    owner = relationship("User", back_populates="urls")


class User(Base):
    """SQLAlchemy model for authenticated users."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    picture = Column(String, nullable=True)
    created_at = Column(DateTime, default=get_utcnow)

    bookmarks = relationship("Bookmark", back_populates="owner", cascade="all, delete-orphan")
    urls = relationship("URL", back_populates="owner")


class Bookmark(Base):
    """SQLAlchemy model for user bookmarks."""

    __tablename__ = "bookmarks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    url = Column(String, nullable=False)
    title = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    tags = Column(String, nullable=True)  # comma-separated
    created_at = Column(DateTime, default=get_utcnow)

    owner = relationship("User", back_populates="bookmarks")
