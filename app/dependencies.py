from typing import Optional

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError

from app.database import get_db
from app.auth import decode_jwt
from app.models import User

# tokenUrl is only used for Swagger UI's "Authorize" dialog
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/google", auto_error=True)
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/auth/google", auto_error=False)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    FastAPI dependency — extracts and verifies the JWT from the
    Authorization header, then returns the corresponding User.
    Raises 401 if the token is missing, invalid, or the user no longer exists.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_jwt(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    return user


def get_optional_user(
    token: Optional[str] = Depends(oauth2_scheme_optional),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """
    Same as get_current_user but returns None instead of 401
    when no token is provided.  Useful for routes that work
    with or without authentication.
    """
    if token is None:
        return None
    try:
        payload = decode_jwt(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
    except JWTError:
        return None

    return db.query(User).filter(User.id == int(user_id)).first()
