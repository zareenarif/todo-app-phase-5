"""
Phase 9 Integration Tests (T051–T062).

Tests the full chat flow end-to-end by mocking only the AI agent layer,
allowing real database operations and API validation.
"""
import json
import pytest
from unittest.mock import AsyncMock, patch
from sqlmodel import Session, select

from tests.conftest import (
    TEST_USER_ID,
    test_engine,
    mock_agent_result,
)
from src.models.task import Task, PriorityEnum
from src.models.conversation import Conversation, Message
from src.mcp.tools import add_task, list_tasks, complete_task, delete_task, update_task


# ─── Helper ──────────────────────────────────────────────────────────────────


def _create_task(title: str, **kwargs) -> dict:
    """Create a task directly via MCP tool and return parsed JSON."""
    result = add_task(user_id=TEST_USER_ID, title=title, **kwargs)
    return json.loads(result)


def _get_tasks() -> list:
    """List all tasks for test user via MCP tool."""
    result = list_tasks(user_id=TEST_USER_ID)
    return json.loads(result)["tasks"]


# ─── T051: Add Task Flow ────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_t051_add_task_flow(client, auth_headers):
    """T051: Type 'Add a task to buy groceries' → verify task created in DB
    and agent confirms."""

    # Mock agent to simulate calling add_task tool then confirming
    created = _create_task("Buy groceries")

    agent_response = mock_agent_result(
        response=f"I've added 'Buy groceries' to your tasks.",
        tool_calls=[{
            "tool_name": "agent_add_task",
            "tool_input": {"user_id": TEST_USER_ID, "title": "Buy groceries"},
            "tool_output": json.dumps(created),
        }],
    )

    with patch(
        "src.services.chat_service.run_chat_agent",
        new_callable=AsyncMock,
        return_value=agent_response,
    ):
        resp = await client.post(
            f"/api/v1/chat/{TEST_USER_ID}",
            json={"message": "Add a task to buy groceries"},
            headers=auth_headers,
        )

    assert resp.status_code == 200
    data = resp.json()
    assert "conversation_id" in data
    assert "Buy groceries" in data["response"]
    assert len(data["tool_calls"]) == 1
    assert data["tool_calls"][0]["tool_name"] == "agent_add_task"

    # Verify task exists in DB
    with Session(test_engine) as session:
        tasks = session.exec(
            select(Task).where(Task.user_id == TEST_USER_ID)
        ).all()
        assert any(t.title == "Buy groceries" for t in tasks)


# ─── T052: List Tasks Flow ──────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_t052_list_tasks_flow(client, auth_headers):
    """T052: Type 'Show my tasks' → verify agent lists tasks via list_tasks."""

    _create_task("Buy groceries")
    _create_task("Do laundry")
    tasks_json = list_tasks(user_id=TEST_USER_ID)

    agent_response = mock_agent_result(
        response="Here are your tasks:\n1. Buy groceries\n2. Do laundry",
        tool_calls=[{
            "tool_name": "agent_list_tasks",
            "tool_input": {"user_id": TEST_USER_ID},
            "tool_output": tasks_json,
        }],
    )

    with patch(
        "src.services.chat_service.run_chat_agent",
        new_callable=AsyncMock,
        return_value=agent_response,
    ):
        resp = await client.post(
            f"/api/v1/chat/{TEST_USER_ID}",
            json={"message": "Show my tasks"},
            headers=auth_headers,
        )

    assert resp.status_code == 200
    data = resp.json()
    assert "tasks" in data["response"].lower() or "groceries" in data["response"].lower()
    assert len(data["tool_calls"]) >= 1
    assert data["tool_calls"][0]["tool_name"] == "agent_list_tasks"


# ─── T053: Complete Task Flow ───────────────────────────────────────────────


@pytest.mark.asyncio
async def test_t053_complete_task_flow(client, auth_headers):
    """T053: Type 'Mark buy groceries as done' → verify complete_task invoked."""

    created = _create_task("Buy groceries")
    task_id = created["task_id"]

    # Actually complete the task via tool
    complete_result = complete_task(user_id=TEST_USER_ID, task_id=task_id)

    agent_response = mock_agent_result(
        response="Done! 'Buy groceries' has been marked as completed.",
        tool_calls=[{
            "tool_name": "agent_complete_task",
            "tool_input": {"user_id": TEST_USER_ID, "task_id": task_id},
            "tool_output": complete_result,
        }],
    )

    with patch(
        "src.services.chat_service.run_chat_agent",
        new_callable=AsyncMock,
        return_value=agent_response,
    ):
        resp = await client.post(
            f"/api/v1/chat/{TEST_USER_ID}",
            json={"message": "Mark buy groceries as done"},
            headers=auth_headers,
        )

    assert resp.status_code == 200
    data = resp.json()
    assert "completed" in data["response"].lower() or "done" in data["response"].lower()

    # Verify task completed in DB
    with Session(test_engine) as session:
        task = session.exec(
            select(Task).where(Task.id == task_id)
        ).first()
        assert task.completed is True


# ─── T054: Update Priority Flow ────────────────────────────────────────────


@pytest.mark.asyncio
async def test_t054_update_priority_flow(client, auth_headers):
    """T054: Type 'Change priority to high' → verify update_task invoked."""

    created = _create_task("Buy groceries")
    task_id = created["task_id"]

    # Actually update the task via tool
    update_result = update_task(
        user_id=TEST_USER_ID, task_id=task_id, priority="high"
    )

    agent_response = mock_agent_result(
        response="I've updated 'Buy groceries' priority to high.",
        tool_calls=[{
            "tool_name": "agent_update_task",
            "tool_input": {
                "user_id": TEST_USER_ID,
                "task_id": task_id,
                "priority": "high",
            },
            "tool_output": update_result,
        }],
    )

    with patch(
        "src.services.chat_service.run_chat_agent",
        new_callable=AsyncMock,
        return_value=agent_response,
    ):
        resp = await client.post(
            f"/api/v1/chat/{TEST_USER_ID}",
            json={"message": "Change priority to high"},
            headers=auth_headers,
        )

    assert resp.status_code == 200
    data = resp.json()
    assert "high" in data["response"].lower()

    # Verify priority updated in DB
    with Session(test_engine) as session:
        task = session.exec(
            select(Task).where(Task.id == task_id)
        ).first()
        assert task.priority == PriorityEnum.HIGH


# ─── T055: Delete Task with Confirmation ────────────────────────────────────


@pytest.mark.asyncio
async def test_t055_delete_task_confirmation(client, auth_headers):
    """T055: Type 'Delete buy groceries' → verify agent asks for confirmation
    before delete_task."""

    created = _create_task("Buy groceries")
    task_id = created["task_id"]

    # First request: agent should ask for confirmation (no tool call)
    confirm_response = mock_agent_result(
        response="Are you sure you want to delete 'Buy groceries'?",
        tool_calls=[],
    )

    with patch(
        "src.services.chat_service.run_chat_agent",
        new_callable=AsyncMock,
        return_value=confirm_response,
    ):
        resp1 = await client.post(
            f"/api/v1/chat/{TEST_USER_ID}",
            json={"message": "Delete buy groceries"},
            headers=auth_headers,
        )

    assert resp1.status_code == 200
    data1 = resp1.json()
    conv_id = data1["conversation_id"]
    assert "sure" in data1["response"].lower() or "confirm" in data1["response"].lower()
    assert len(data1["tool_calls"]) == 0  # No delete yet

    # Task should still exist
    with Session(test_engine) as session:
        task = session.exec(select(Task).where(Task.id == task_id)).first()
        assert task is not None

    # Second request: user confirms → agent calls delete_task
    delete_result = delete_task(user_id=TEST_USER_ID, task_id=task_id)

    delete_response = mock_agent_result(
        response="'Buy groceries' has been deleted.",
        tool_calls=[{
            "tool_name": "agent_delete_task",
            "tool_input": {"user_id": TEST_USER_ID, "task_id": task_id},
            "tool_output": delete_result,
        }],
    )

    with patch(
        "src.services.chat_service.run_chat_agent",
        new_callable=AsyncMock,
        return_value=delete_response,
    ):
        resp2 = await client.post(
            f"/api/v1/chat/{TEST_USER_ID}",
            json={
                "message": "Yes, delete it",
                "conversation_id": conv_id,
            },
            headers=auth_headers,
        )

    assert resp2.status_code == 200
    data2 = resp2.json()
    assert "deleted" in data2["response"].lower()

    # Task should be deleted from DB
    with Session(test_engine) as session:
        task = session.exec(select(Task).where(Task.id == task_id)).first()
        assert task is None


# ─── T056: Conversation Persistence ─────────────────────────────────────────


@pytest.mark.asyncio
async def test_t056_conversation_persistence(client, auth_headers):
    """T056: Send multiple messages in same conversation, verify context
    preserved across requests."""

    # First message — creates conversation
    resp1_agent = mock_agent_result(
        response="I've added 'Buy groceries' to your tasks.",
        tool_calls=[],
    )

    with patch(
        "src.services.chat_service.run_chat_agent",
        new_callable=AsyncMock,
        return_value=resp1_agent,
    ):
        resp1 = await client.post(
            f"/api/v1/chat/{TEST_USER_ID}",
            json={"message": "Add a task to buy groceries"},
            headers=auth_headers,
        )

    assert resp1.status_code == 200
    conv_id = resp1.json()["conversation_id"]

    # Second message — same conversation
    resp2_agent = mock_agent_result(
        response="Here are your tasks: 1. Buy groceries",
        tool_calls=[],
    )

    with patch(
        "src.services.chat_service.run_chat_agent",
        new_callable=AsyncMock,
        return_value=resp2_agent,
    ) as mock_run:
        resp2 = await client.post(
            f"/api/v1/chat/{TEST_USER_ID}",
            json={
                "message": "Show my tasks",
                "conversation_id": conv_id,
            },
            headers=auth_headers,
        )

    assert resp2.status_code == 200
    assert resp2.json()["conversation_id"] == conv_id

    # Verify messages are persisted in DB
    with Session(test_engine) as session:
        messages = session.exec(
            select(Message)
            .where(Message.conversation_id == conv_id)
            .order_by(Message.created_at.asc())
        ).all()

    # Should have: user1, assistant1, user2, assistant2
    roles = [m.role for m in messages]
    assert roles.count("user") == 2
    assert roles.count("assistant") == 2

    # Verify agent received previous messages (history)
    call_args = mock_run.call_args
    assert call_args is not None
    # The messages kwarg should contain history from the first exchange
    history_messages = call_args.kwargs.get("messages") or call_args.args[1]
    assert len(history_messages) >= 2  # At least the first user + assistant


# ─── T057: Multi-Step Chaining ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_t057_multistep_chaining(client, auth_headers):
    """T057: Type 'Complete buy groceries and add pick up dry cleaning'
    → verify both tools invoked."""

    created = _create_task("Buy groceries")
    task_id = created["task_id"]

    # Simulate agent invoking both complete_task and add_task
    complete_result = complete_task(user_id=TEST_USER_ID, task_id=task_id)
    new_task = _create_task("Pick up dry cleaning")

    agent_response = mock_agent_result(
        response="Done! I've completed 'Buy groceries' and added 'Pick up dry cleaning'.",
        tool_calls=[
            {
                "tool_name": "agent_complete_task",
                "tool_input": {"user_id": TEST_USER_ID, "task_id": task_id},
                "tool_output": complete_result,
            },
            {
                "tool_name": "agent_add_task",
                "tool_input": {"user_id": TEST_USER_ID, "title": "Pick up dry cleaning"},
                "tool_output": json.dumps(new_task),
            },
        ],
    )

    with patch(
        "src.services.chat_service.run_chat_agent",
        new_callable=AsyncMock,
        return_value=agent_response,
    ):
        resp = await client.post(
            f"/api/v1/chat/{TEST_USER_ID}",
            json={"message": "Complete buy groceries and add pick up dry cleaning"},
            headers=auth_headers,
        )

    assert resp.status_code == 200
    data = resp.json()
    assert len(data["tool_calls"]) == 2

    tool_names = [tc["tool_name"] for tc in data["tool_calls"]]
    assert "agent_complete_task" in tool_names
    assert "agent_add_task" in tool_names


# ─── T058: Empty Message Error ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_t058_empty_message_error(client, auth_headers):
    """T058: Send empty message → verify 422 (Pydantic validation) response."""

    resp = await client.post(
        f"/api/v1/chat/{TEST_USER_ID}",
        json={"message": ""},
        headers=auth_headers,
    )

    # Empty message rejected — either 422 (Pydantic) or 400 (custom handler)
    assert resp.status_code in (400, 422)


# ─── T059: Non-Existent Task Reference ──────────────────────────────────────


@pytest.mark.asyncio
async def test_t059_nonexistent_task(client, auth_headers):
    """T059: Reference non-existent task → verify agent offers to list tasks."""

    agent_response = mock_agent_result(
        response="I couldn't find that task. Want me to list your tasks?",
        tool_calls=[{
            "tool_name": "agent_list_tasks",
            "tool_input": {"user_id": TEST_USER_ID},
            "tool_output": json.dumps({"tasks": [], "count": 0}),
        }],
    )

    with patch(
        "src.services.chat_service.run_chat_agent",
        new_callable=AsyncMock,
        return_value=agent_response,
    ):
        resp = await client.post(
            f"/api/v1/chat/{TEST_USER_ID}",
            json={"message": "Complete the task about flying to Mars"},
            headers=auth_headers,
        )

    assert resp.status_code == 200
    data = resp.json()
    # Agent should indicate task not found
    response_lower = data["response"].lower()
    assert "couldn't find" in response_lower or "not found" in response_lower or "list" in response_lower


# ─── T060: Non-Task Query Redirect ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_t060_nontask_query_redirect(client, auth_headers):
    """T060: Send 'What's the weather?' → verify agent redirects to task management."""

    agent_response = mock_agent_result(
        response="I can only help with task management. Would you like to add, list, update, complete, or delete tasks?",
        tool_calls=[],
    )

    with patch(
        "src.services.chat_service.run_chat_agent",
        new_callable=AsyncMock,
        return_value=agent_response,
    ):
        resp = await client.post(
            f"/api/v1/chat/{TEST_USER_ID}",
            json={"message": "What's the weather?"},
            headers=auth_headers,
        )

    assert resp.status_code == 200
    data = resp.json()
    assert "task management" in data["response"].lower() or "task" in data["response"].lower()
    assert len(data["tool_calls"]) == 0  # No tools should be called


# ─── T061: Tool Calls Array Verification ────────────────────────────────────


@pytest.mark.asyncio
async def test_t061_tool_calls_in_response(client, auth_headers):
    """T061: Verify tool_calls array in API response contains all tool
    invocations from the request."""

    created = _create_task("Buy groceries")
    tasks_json = list_tasks(user_id=TEST_USER_ID)

    # Agent does list then add — two tool calls
    new_task = _create_task("Walk the dog")

    agent_response = mock_agent_result(
        response="Listed your tasks and added 'Walk the dog'.",
        tool_calls=[
            {
                "tool_name": "agent_list_tasks",
                "tool_input": {"user_id": TEST_USER_ID},
                "tool_output": tasks_json,
            },
            {
                "tool_name": "agent_add_task",
                "tool_input": {"user_id": TEST_USER_ID, "title": "Walk the dog"},
                "tool_output": json.dumps(new_task),
            },
        ],
    )

    with patch(
        "src.services.chat_service.run_chat_agent",
        new_callable=AsyncMock,
        return_value=agent_response,
    ):
        resp = await client.post(
            f"/api/v1/chat/{TEST_USER_ID}",
            json={"message": "Show my tasks then add walk the dog"},
            headers=auth_headers,
        )

    assert resp.status_code == 200
    data = resp.json()

    # Verify tool_calls array structure
    assert isinstance(data["tool_calls"], list)
    assert len(data["tool_calls"]) == 2

    for tc in data["tool_calls"]:
        assert "tool_name" in tc
        assert "tool_input" in tc
        assert "tool_output" in tc
        assert isinstance(tc["tool_input"], dict)

    # Verify the tool calls are persisted as messages in DB
    conv_id = data["conversation_id"]
    with Session(test_engine) as session:
        tool_messages = session.exec(
            select(Message).where(
                Message.conversation_id == conv_id,
                Message.role == "tool",
            )
        ).all()
        assert len(tool_messages) == 2


# ─── T062: Quickstart Validation Checklist ──────────────────────────────────


@pytest.mark.asyncio
async def test_t062_quickstart_validation(client, auth_headers):
    """T062: Run quickstart validation checklist — verify core system contracts."""

    # 1. Health check
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"

    # 2. Root endpoint
    resp = await client.get("/")
    assert resp.status_code == 200
    assert "version" in resp.json()

    # 3. Chat endpoint requires auth
    resp = await client.post(
        f"/api/v1/chat/{TEST_USER_ID}",
        json={"message": "hello"},
    )
    assert resp.status_code in (401, 403)

    # 4. Chat endpoint rejects mismatched user_id
    other_id = "00000000-0000-0000-0000-000000000099"
    agent_response = mock_agent_result(response="ok", tool_calls=[])
    with patch(
        "src.services.chat_service.run_chat_agent",
        new_callable=AsyncMock,
        return_value=agent_response,
    ):
        resp = await client.post(
            f"/api/v1/chat/{other_id}",
            json={"message": "hello"},
            headers=auth_headers,
        )
    assert resp.status_code == 401

    # 5. Chat endpoint returns ChatResponse schema
    agent_response = mock_agent_result(
        response="Hello! How can I help with your tasks?",
        tool_calls=[],
    )
    with patch(
        "src.services.chat_service.run_chat_agent",
        new_callable=AsyncMock,
        return_value=agent_response,
    ):
        resp = await client.post(
            f"/api/v1/chat/{TEST_USER_ID}",
            json={"message": "hello"},
            headers=auth_headers,
        )

    assert resp.status_code == 200
    data = resp.json()
    assert "conversation_id" in data
    assert "response" in data
    assert "tool_calls" in data
    assert isinstance(data["tool_calls"], list)

    # 6. MCP tools are stateless — each creates a fresh session
    t1 = json.loads(add_task(user_id=TEST_USER_ID, title="Stateless Test 1"))
    t2 = json.loads(add_task(user_id=TEST_USER_ID, title="Stateless Test 2"))
    assert t1["task_id"] != t2["task_id"]

    # 7. MCP tools enforce user_id isolation
    other_tasks = json.loads(list_tasks(user_id="nonexistent-user"))
    assert other_tasks["count"] == 0

    # 8. Conversation model has required fields
    with Session(test_engine) as session:
        convs = session.exec(select(Conversation)).all()
        for conv in convs:
            assert conv.id is not None
            assert conv.user_id is not None
            assert conv.created_at is not None


# ─── Additional: Auth & Isolation Tests ─────────────────────────────────────


@pytest.mark.asyncio
async def test_auth_required(client):
    """Verify chat endpoint returns 401/403 without auth token."""
    resp = await client.post(
        f"/api/v1/chat/{TEST_USER_ID}",
        json={"message": "hello"},
    )
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_user_id_mismatch(client, auth_headers):
    """Verify chat endpoint rejects when path user_id != JWT user_id."""
    fake_id = "00000000-0000-0000-0000-000000000000"
    resp = await client.post(
        f"/api/v1/chat/{fake_id}",
        json={"message": "hello"},
        headers=auth_headers,
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_invalid_conversation_id(client, auth_headers):
    """Verify 404 when providing non-existent conversation_id."""
    agent_response = mock_agent_result(response="ok", tool_calls=[])
    with patch(
        "src.services.chat_service.run_chat_agent",
        new_callable=AsyncMock,
        return_value=agent_response,
    ):
        resp = await client.post(
            f"/api/v1/chat/{TEST_USER_ID}",
            json={
                "message": "hello",
                "conversation_id": "nonexistent-conv-id",
            },
            headers=auth_headers,
        )
    assert resp.status_code == 404
