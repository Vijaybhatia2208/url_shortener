import string
import random
from sqlalchemy.orm import Session
from app.models import URL
from app.schemas import URLCreate
from app.config import get_settings


settings = get_settings()


def generate_short_code(length: int) -> str:
    """Generate a random string of fixed length."""
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))


def create_short_url(db: Session, url: URLCreate) -> URL:
    """Create a new shortened URL in the database."""
    # Handle the HttpUrl from Pydantic which is an object in v2
    original_url_str = str(url.original_url)
    
    # Generate a unique code
    while True:
        code = generate_short_code(settings.SHORT_CODE_LENGTH)
        # Check if it already exists (collision)
        existing = db.query(URL).filter(URL.short_code == code).first()
        if not existing:
            break

    db_url = URL(
        short_code=code,
        original_url=original_url_str
    )
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    return db_url


def get_url_by_code(db: Session, short_code: str) -> URL | None:
    """Retrieve a URL by its short code."""
    return db.query(URL).filter(URL.short_code == short_code).first()


def increment_clicks(db: Session, db_url: URL) -> URL:
    """Increment the click counter for a URL."""
    db_url.clicks += 1
    db.commit()
    db.refresh(db_url)
    return db_url
