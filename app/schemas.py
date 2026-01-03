from pydantic import BaseModel, HttpUrl
from datetime import datetime


class URLBase(BaseModel):
    """Properties shared across URL schemas."""
    original_url: HttpUrl


class URLCreate(URLBase):
    """Schema for parsing incoming URL creation requests."""
    pass


class URLResponse(URLBase):
    """Schema for validating and serializing URL responses."""
    short_code: str
    short_url: str
    clicks: int
    created_at: datetime

    class Config:
        from_attributes = True  # Allows Pydantic to read from SQLAlchemy ORM models
