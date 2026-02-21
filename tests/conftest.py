"""
Shared test fixtures for the URL shortener tests.
Uses a test SQLite database so tests are fast and isolated.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.models import User
from app.auth import create_jwt
from app.main import app

# Test SQLite DB
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_database():
    """Create all tables before each test, drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    """Yield a clean DB session for each test."""
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session):
    """FastAPI TestClient with the DB dependency overridden to use the test DB."""
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Insert and return a test user."""
    user = User(email="test@example.com", name="Test User", picture=None)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def second_user(db_session):
    """Insert and return a second test user for isolation tests."""
    user = User(email="other@example.com", name="Other User", picture=None)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user):
    """Authorization headers with a valid JWT for test_user."""
    token = create_jwt(test_user.id, test_user.email)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def second_auth_headers(second_user):
    """Authorization headers with a valid JWT for second_user."""
    token = create_jwt(second_user.id, second_user.email)
    return {"Authorization": f"Bearer {token}"}
