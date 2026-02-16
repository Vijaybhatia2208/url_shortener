from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import GoogleAuthRequest, AuthResponse, UserResponse
from app.auth import verify_google_token, create_jwt
from app.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/google", response_model=AuthResponse)
def google_login(body: GoogleAuthRequest, db: Session = Depends(get_db)):
    """
    Authenticate with a Google ID token.

    1. Verifies the token against Google's servers.
    2. Upserts the user (creates if new, updates name/picture if returning).
    3. Returns a JWT access token + user profile.
    """
    try:
        google_data = verify_google_token(body.token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        )

    email = google_data["email"]
    name = google_data.get("name")
    picture = google_data.get("picture")

    # Upsert user
    user = db.query(User).filter(User.email == email).first()
    if user:
        # Update profile fields that may have changed on Google's side
        user.name = name
        user.picture = picture
        db.commit()
        db.refresh(user)
    else:
        user = User(email=email, name=name, picture=picture)
        db.add(user)
        db.commit()
        db.refresh(user)

    access_token = create_jwt(user.id, user.email)

    return AuthResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Return the profile of the currently authenticated user."""
    return UserResponse.model_validate(current_user)
