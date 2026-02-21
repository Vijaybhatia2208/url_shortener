from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import BookmarkCreate, BookmarkUpdate, BookmarkResponse
from app.crud import (
    create_bookmark,
    get_bookmarks,
    get_bookmark_by_id,
    update_bookmark,
    delete_bookmark,
)
from app.dependencies import get_current_user

router = APIRouter(prefix="/bookmarks", tags=["Bookmarks"])


@router.post("", response_model=BookmarkResponse, status_code=status.HTTP_201_CREATED)
def save_bookmark(
    data: BookmarkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Save a new bookmark for the authenticated user."""
    bookmark = create_bookmark(db, current_user.id, data)
    return BookmarkResponse.from_model(bookmark)


@router.get("", response_model=list[BookmarkResponse])
def list_bookmarks(
    search: Optional[str] = None,
    tag: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List the authenticated user's bookmarks.

    Optional query params:
    - **search**: filter by keyword in title, url, or description
    - **tag**: filter by tag name
    """
    bookmarks = get_bookmarks(db, current_user.id, search=search, tag=tag)
    return [BookmarkResponse.from_model(bm) for bm in bookmarks]


@router.put("/{bookmark_id}", response_model=BookmarkResponse)
def edit_bookmark(
    bookmark_id: int,
    data: BookmarkUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an existing bookmark. Only the provided fields are changed."""
    bookmark = get_bookmark_by_id(db, bookmark_id)
    if not bookmark or bookmark.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bookmark not found")

    updated = update_bookmark(db, bookmark, data)
    return BookmarkResponse.from_model(updated)


@router.delete("/{bookmark_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_bookmark(
    bookmark_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a bookmark."""
    bookmark = get_bookmark_by_id(db, bookmark_id)
    if not bookmark or bookmark.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bookmark not found")

    delete_bookmark(db, bookmark)
