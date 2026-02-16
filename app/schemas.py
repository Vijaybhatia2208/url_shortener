from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional


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


# ── Auth Schemas ─────────────────────────────────────────────


class GoogleAuthRequest(BaseModel):
    """Request body for Google OAuth2 login."""
    token: str


class UserResponse(BaseModel):
    """Public user profile."""
    id: int
    email: str
    name: Optional[str] = None
    picture: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    """Response returned after successful authentication."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
