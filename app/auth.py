from datetime import datetime, timedelta, timezone

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from jose import JWTError, jwt

from app.config import get_settings

settings = get_settings()


def verify_google_token(token: str) -> dict:
    """
    Verify a Google ID token and return the decoded payload.
    Raises ValueError if the token is invalid or expired.
    """
    try:
        payload = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )
        return {
            "email": payload["email"],
            "name": payload.get("name"),
            "picture": payload.get("picture"),
        }
    except Exception as exc:
        raise ValueError(f"Invalid Google token: {exc}") from exc


def create_jwt(user_id: int, email: str) -> str:
    """Create a signed JWT containing the user's id and email."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": expire,
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_jwt(token: str) -> dict:
    """
    Decode and verify a JWT. Returns the payload dict.
    Raises JWTError on invalid / expired tokens.
    """
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
