from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import URLCreate, URLResponse, DestinationResponse
from app.config import get_settings
from app.crud import create_short_url, get_url_by_code, increment_clicks, get_urls_by_user
from app.dependencies import get_current_user, get_optional_user


router = APIRouter()
settings = get_settings()


def get_full_url(short_code: str) -> str:
    """Helper to construct the full short URL focusing on the frontend domain."""
    base_url = settings.FRONTEND_URL.rstrip("/")
    return f"{base_url}/short/{short_code}"


@router.post("/shorten", response_model=URLResponse)
def shorten_url(
    url: URLCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """Creates a new short URL. If authenticated, the URL is linked to the user."""
    user_id = current_user.id if current_user else None
    db_url = create_short_url(db, url, user_id=user_id)
    
    return URLResponse(
        original_url=db_url.original_url,
        short_code=db_url.short_code,
        short_url=get_full_url(db_url.short_code),
        clicks=db_url.clicks,
        created_at=db_url.created_at
    )


@router.get("/my-urls", response_model=list[URLResponse])
def list_my_urls(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all shortened URLs created by the authenticated user."""
    urls = get_urls_by_user(db, current_user.id)
    return [
        URLResponse(
            original_url=u.original_url,
            short_code=u.short_code,
            short_url=get_full_url(u.short_code),
            clicks=u.clicks,
            created_at=u.created_at,
        )
        for u in urls
    ]


@router.get("/{short_code}", response_model=DestinationResponse)
def redirect_to_url(short_code: str, db: Session = Depends(get_db)):
    """Returns the original URL if the short code exists so frontend can handle redirect."""
    db_url = get_url_by_code(db, short_code)
    if not db_url:
        raise HTTPException(status_code=404, detail="Short URL not found")
        
    # Increment click count
    increment_clicks(db, db_url)
    
    return DestinationResponse(original_url=db_url.original_url)


@router.get("/info/{short_code}", response_model=URLResponse)
def get_url_info(short_code: str, db: Session = Depends(get_db)):
    """Returns analytics/info about a specific short URL."""
    db_url = get_url_by_code(db, short_code)
    if not db_url:
        raise HTTPException(status_code=404, detail="Short URL not found")
        
    return URLResponse(
        original_url=db_url.original_url,
        short_code=db_url.short_code,
        short_url=get_full_url(db_url.short_code),
        clicks=db_url.clicks,
        created_at=db_url.created_at
    )
