"""
Shared test fixtures for integration tests.

Uses SQLite in-memory database and mocks the AI agent
to avoid external API dependencies during testing.
"""
import os
import json
import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime
from uuid import uuid4

# Override DATABASE_URL before any app imports
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["BETTER_AUTH_SECRET"] = "test-secret-key-for-jwt-signing"
os.environ["GROQ_API_KEY"] = "test-groq-key"
os.environ["OPENAI_API_KEY"] = "test-openai-key"

from jose import jwt
from httpx import AsyncClient, ASGITransport
from sqlmodel import SQLModel, Session, create_engine

# Override the engine before importing app modules
import src.core.database as db_module
import src.core.config as config_module

test_engine = create_engine(
    "sqlite:///./test.db",
    echo=False,
    connect_args={"check_same_thread": False},
)
db_module.engine = test_engine

# Now import app modules (they use the overridden engine)
from src.main import app
from src.models.user import User
from src.models.task import Task, PriorityEnum
from src.models.conversation import Conversation, Message
from src.agents.chat_agent import AgentResult

# Also patch the engine used by MCP tools and chat service
import src.mcp.tools as tools_module
import src.services.chat_service as chat_service_module
tools_module.engine = test_engine
chat_service_module.engine = test_engine


TEST_USER_ID = str(uuid4())
TEST_USER_EMAIL = "testuser@example.com"


def create_test_jwt(user_id: str) -> str:
    """Create a valid JWT token for testing."""
    payload = {
        "user_id": user_id,
        "exp": datetime(2099, 1, 1).timestamp(),
    }
    return jwt.encode(payload, "test-secret-key-for-jwt-signing", algorithm="HS256")


@pytest.fixture(autouse=True)
def setup_database():
    """Create all tables before each test and drop after."""
    SQLModel.metadata.create_all(test_engine)

    # Ensure test user exists
    with Session(test_engine) as session:
        user = session.get(User, TEST_USER_ID)
        if not user:
            user = User(
                id=TEST_USER_ID,
                email=TEST_USER_EMAIL,
                name="Test User",
                password_hash="hashed",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            session.add(user)
            session.commit()

    yield

    SQLModel.metadata.drop_all(test_engine)


@pytest.fixture
def auth_headers():
    """Return Authorization headers with a valid JWT."""
    token = create_test_jwt(TEST_USER_ID)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def other_user_headers():
    """Return Authorization headers for a different user."""
    other_id = str(uuid4())
    token = create_test_jwt(other_id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def client():
    """Async HTTP client for testing FastAPI endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


def mock_agent_result(response: str, tool_calls: list = None) -> AgentResult:
    """Create a mock AgentResult."""
    return AgentResult(
        response=response,
        tool_calls=tool_calls or [],
    )
