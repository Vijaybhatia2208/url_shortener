"""
Tests for bookmark Pydantic schemas — validation and tag conversion.
"""
import pytest
from app.schemas import BookmarkCreate, BookmarkUpdate, BookmarkResponse
from app.models import Bookmark
from datetime import datetime, timezone


class TestBookmarkCreate:
    def test_all_fields(self):
        schema = BookmarkCreate(
            url="https://example.com",
            title="Example",
            description="Desc",
            tags=["a", "b"],
        )
        assert schema.url == "https://example.com"
        assert schema.tags == ["a", "b"]

    def test_only_url_required(self):
        schema = BookmarkCreate(url="https://example.com")
        assert schema.url == "https://example.com"
        assert schema.title is None
        assert schema.description is None
        assert schema.tags is None

    def test_url_required(self):
        with pytest.raises(Exception):
            BookmarkCreate()


class TestBookmarkUpdate:
    def test_all_optional(self):
        schema = BookmarkUpdate()
        assert schema.url is None
        assert schema.title is None
        assert schema.description is None
        assert schema.tags is None

    def test_partial(self):
        schema = BookmarkUpdate(title="New Title")
        data = schema.model_dump(exclude_unset=True)
        assert data == {"title": "New Title"}

    def test_tags_list(self):
        schema = BookmarkUpdate(tags=["x", "y"])
        assert schema.tags == ["x", "y"]


class TestBookmarkResponse:
    def test_from_model_with_tags(self):
        """Test the from_model classmethod splits comma-separated tags."""
        # Create a mock-like bookmark object
        class FakeBookmark:
            id = 1
            user_id = 10
            url = "https://example.com"
            title = "Test"
            description = "Desc"
            tags = "python,dev,api"
            created_at = datetime(2026, 1, 1, tzinfo=timezone.utc)

        resp = BookmarkResponse.from_model(FakeBookmark())
        assert resp.tags == ["python", "dev", "api"]
        assert resp.id == 1
        assert resp.user_id == 10

    def test_from_model_without_tags(self):
        class FakeBookmark:
            id = 2
            user_id = 10
            url = "https://notags.com"
            title = None
            description = None
            tags = None
            created_at = datetime(2026, 1, 1, tzinfo=timezone.utc)

        resp = BookmarkResponse.from_model(FakeBookmark())
        assert resp.tags is None
