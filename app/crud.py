import string
import random
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models import URL, Bookmark
from app.schemas import URLCreate, BookmarkCreate, BookmarkUpdate
from app.config import get_settings


settings = get_settings()


def generate_short_code(length: int) -> str:
    """Generate a random string of fixed length."""
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))


def create_short_url(db: Session, url: URLCreate, user_id: Optional[int] = None) -> URL:
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
        original_url=original_url_str,
        user_id=user_id,
    )
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    return db_url


def get_url_by_code(db: Session, short_code: str) -> Optional[URL]:
    """Retrieve a URL by its short code."""
    return db.query(URL).filter(URL.short_code == short_code).first()


def increment_clicks(db: Session, db_url: URL) -> URL:
    """Increment the click counter for a URL."""
    db_url.clicks += 1
    db.commit()
    db.refresh(db_url)
    return db_url


def get_urls_by_user(db: Session, user_id: int) -> list[URL]:
    """List all shortened URLs owned by a user."""
    return db.query(URL).filter(URL.user_id == user_id).order_by(URL.created_at.desc()).all()


# ── Bookmark CRUD ────────────────────────────────────────────


def create_bookmark(db: Session, user_id: int, data: BookmarkCreate) -> Bookmark:
    """Create a new bookmark for a user."""
    tags_str = ",".join(data.tags) if data.tags else None
    bookmark = Bookmark(
        user_id=user_id,
        url=data.url,
        title=data.title,
        description=data.description,
        tags=tags_str,
    )
    db.add(bookmark)
    db.commit()
    db.refresh(bookmark)
    return bookmark


def get_bookmarks(
    db: Session,
    user_id: int,
    search: Optional[str] = None,
    tag: Optional[str] = None,
) -> list[Bookmark]:
    """List bookmarks for a user, optionally filtered by search keyword or tag."""
    query = db.query(Bookmark).filter(Bookmark.user_id == user_id)

    if search:
        pattern = f"%{search}%"
        query = query.filter(
            or_(
                Bookmark.title.ilike(pattern),
                Bookmark.url.ilike(pattern),
                Bookmark.description.ilike(pattern),
            )
        )

    if tag:
        # Match tag in comma-separated string
        query = query.filter(Bookmark.tags.ilike(f"%{tag}%"))

    return query.order_by(Bookmark.created_at.desc()).all()


def get_bookmark_by_id(db: Session, bookmark_id: int) -> Optional[Bookmark]:
    """Retrieve a single bookmark by its id."""
    return db.query(Bookmark).filter(Bookmark.id == bookmark_id).first()


def update_bookmark(db: Session, bookmark: Bookmark, data: BookmarkUpdate) -> Bookmark:
    """Update bookmark fields (only those provided)."""
    update_data = data.model_dump(exclude_unset=True)

    if "tags" in update_data:
        tags_value = update_data.pop("tags")
        bookmark.tags = ",".join(tags_value) if tags_value else None

    for field, value in update_data.items():
        setattr(bookmark, field, value)

    db.commit()
    db.refresh(bookmark)
    return bookmark


def delete_bookmark(db: Session, bookmark: Bookmark) -> None:
    """Delete a bookmark."""
    db.delete(bookmark)
    db.commit()
