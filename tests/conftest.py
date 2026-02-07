"""
Pytest configuration and fixtures for backend tests.
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

import sys
import os

# Set test environment variables BEFORE importing app
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("BETTER_AUTH_SECRET", "test-secret-key-for-testing-minimum-32-characters")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:3000")
os.environ.setdefault("DEBUG", "True")
os.environ.setdefault("GROQ_API_KEY", "test-key")
os.environ.setdefault("LLM_PROVIDER", "groq")

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from datetime import datetime
from uuid import uuid4
from src.main import app
from src.core.database import get_session
from src.models.user import User
from src.models.task import Task
from src.api.v1.auth import hash_password, create_access_token


# Create in-memory SQLite database for testing
@pytest.fixture(name="engine")
def engine_fixture():
    """Create a new database engine for each test."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture(name="session")
def session_fixture(engine):
    """Create a new database session for each test."""
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session):
    """Create a test client with overridden database session."""
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="test_user")
def test_user_fixture(session):
    """Create a test user in the database."""
    now = datetime.utcnow()
    user = User(
        id=str(uuid4()),
        email="test@example.com",
        name="Test User",
        password_hash=hash_password("testpassword123"),
        created_at=now,
        updated_at=now,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="test_user_token")
def test_user_token_fixture(test_user):
    """Create an access token for the test user."""
    return create_access_token(test_user.id)


@pytest.fixture(name="auth_headers")
def auth_headers_fixture(test_user_token):
    """Create authorization headers for authenticated requests."""
    return {"Authorization": f"Bearer {test_user_token}"}


@pytest.fixture(name="test_task")
def test_task_fixture(session, test_user):
    """Create a test task in the database."""
    task = Task(
        user_id=test_user.id,
        title="Test Task",
        description="A test task description",
        priority="medium",
        tags=["test", "sample"],
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@pytest.fixture(name="another_user")
def another_user_fixture(session):
    """Create another user for testing authorization."""
    now = datetime.utcnow()
    user = User(
        id=str(uuid4()),
        email="another@example.com",
        name="Another User",
        password_hash=hash_password("anotherpassword"),
        created_at=now,
        updated_at=now,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="another_user_task")
def another_user_task_fixture(session, another_user):
    """Create a task belonging to another user."""
    task = Task(
        user_id=another_user.id,
        title="Another User's Task",
        description="This task belongs to another user",
        priority="high",
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task
