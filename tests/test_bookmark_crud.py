"""
Unit tests for bookmark CRUD functions.
"""
from app.crud import (
    create_bookmark,
    get_bookmarks,
    get_bookmark_by_id,
    update_bookmark,
    delete_bookmark,
)
from app.schemas import BookmarkCreate, BookmarkUpdate


class TestCreateBookmark:
    def test_create_with_all_fields(self, db_session, test_user):
        data = BookmarkCreate(
            url="https://example.com",
            title="Example",
            description="An example site",
            tags=["python", "dev"],
        )
        bm = create_bookmark(db_session, test_user.id, data)

        assert bm.id is not None
        assert bm.user_id == test_user.id
        assert bm.url == "https://example.com"
        assert bm.title == "Example"
        assert bm.description == "An example site"
        assert bm.tags == "python,dev"
        assert bm.created_at is not None

    def test_create_with_only_url(self, db_session, test_user):
        data = BookmarkCreate(url="https://minimal.com")
        bm = create_bookmark(db_session, test_user.id, data)

        assert bm.url == "https://minimal.com"
        assert bm.title is None
        assert bm.description is None
        assert bm.tags is None


class TestGetBookmarks:
    def _seed(self, db_session, user_id):
        bookmarks = [
            BookmarkCreate(url="https://python.org", title="Python", tags=["python"]),
            BookmarkCreate(url="https://fastapi.tiangolo.com", title="FastAPI Docs", tags=["python", "api"]),
            BookmarkCreate(url="https://react.dev", title="React", tags=["frontend"]),
        ]
        for data in bookmarks:
            create_bookmark(db_session, user_id, data)

    def test_list_all_for_user(self, db_session, test_user):
        self._seed(db_session, test_user.id)
        results = get_bookmarks(db_session, test_user.id)
        assert len(results) == 3

    def test_list_isolates_by_user(self, db_session, test_user, second_user):
        self._seed(db_session, test_user.id)
        create_bookmark(db_session, second_user.id, BookmarkCreate(url="https://other.com"))

        assert len(get_bookmarks(db_session, test_user.id)) == 3
        assert len(get_bookmarks(db_session, second_user.id)) == 1

    def test_search_by_title(self, db_session, test_user):
        self._seed(db_session, test_user.id)
        results = get_bookmarks(db_session, test_user.id, search="fastapi")
        assert len(results) == 1
        assert results[0].title == "FastAPI Docs"

    def test_search_by_url(self, db_session, test_user):
        self._seed(db_session, test_user.id)
        results = get_bookmarks(db_session, test_user.id, search="react.dev")
        assert len(results) == 1

    def test_filter_by_tag(self, db_session, test_user):
        self._seed(db_session, test_user.id)
        results = get_bookmarks(db_session, test_user.id, tag="python")
        assert len(results) == 2

    def test_returns_newest_first(self, db_session, test_user):
        self._seed(db_session, test_user.id)
        results = get_bookmarks(db_session, test_user.id)
        # Most recently created should be first
        assert results[0].title == "React"


class TestUpdateBookmark:
    def test_update_title(self, db_session, test_user):
        bm = create_bookmark(db_session, test_user.id, BookmarkCreate(url="https://a.com", title="Old"))
        updated = update_bookmark(db_session, bm, BookmarkUpdate(title="New"))
        assert updated.title == "New"
        assert updated.url == "https://a.com"  # unchanged

    def test_update_tags(self, db_session, test_user):
        bm = create_bookmark(db_session, test_user.id, BookmarkCreate(url="https://a.com", tags=["old"]))
        updated = update_bookmark(db_session, bm, BookmarkUpdate(tags=["new", "tags"]))
        assert updated.tags == "new,tags"

    def test_partial_update_ignores_unset(self, db_session, test_user):
        bm = create_bookmark(
            db_session, test_user.id,
            BookmarkCreate(url="https://a.com", title="Keep", description="Also keep"),
        )
        updated = update_bookmark(db_session, bm, BookmarkUpdate(title="Changed"))
        assert updated.title == "Changed"
        assert updated.description == "Also keep"


class TestDeleteBookmark:
    def test_delete(self, db_session, test_user):
        bm = create_bookmark(db_session, test_user.id, BookmarkCreate(url="https://a.com"))
        bookmark_id = bm.id
        delete_bookmark(db_session, bm)
        assert get_bookmark_by_id(db_session, bookmark_id) is None

    def test_get_nonexistent(self, db_session):
        assert get_bookmark_by_id(db_session, 9999) is None
