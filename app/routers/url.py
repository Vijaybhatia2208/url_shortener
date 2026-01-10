from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import URLCreate, URLResponse
from app.config import get_settings
from app.crud import create_short_url, get_url_by_code, increment_clicks


router = APIRouter()
settings = get_settings()


def get_full_url(short_code: str) -> str:
    """Helper to construct the full short URL."""
    # Ensure BASE_URL doesn't have a trailing slash, then append the code
    base_url = settings.BASE_URL.rstrip("/")
    return f"{base_url}/{short_code}"


@router.post("/shorten", response_model=URLResponse)
def shorten_url(url: URLCreate, db: Session = Depends(get_db)):
    """Creates a new short URL."""
    db_url = create_short_url(db, url)
    
    # We need to construct the URLResponse
    return URLResponse(
        original_url=db_url.original_url,
        short_code=db_url.short_code,
        short_url=get_full_url(db_url.short_code),
        clicks=db_url.clicks,
        created_at=db_url.created_at
    )


@router.get("/{short_code}")
def redirect_to_url(short_code: str, db: Session = Depends(get_db)):
    """Redirects to the original URL if the short code exists."""
    db_url = get_url_by_code(db, short_code)
    if not db_url:
        raise HTTPException(status_code=404, detail="Short URL not found")
        
    # Increment click count
    increment_clicks(db, db_url)
    
    return RedirectResponse(url=db_url.original_url, status_code=307)


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
