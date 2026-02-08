"""
Stateless MCP tool definitions for task operations.

Each tool:
- Receives all context via parameters (stateless)
- Creates a fresh database session per invocation
- Filters by user_id for data isolation
- Returns structured JSON for agent consumption
"""
import json
from datetime import datetime, date
from typing import Optional
from sqlmodel import Session, select
from src.core.database import engine
from src.models.task import Task, PriorityEnum
from src.mcp import mcp_server


@mcp_server.tool()
def add_task(
    user_id: str,
    title: str,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    due_date: Optional[str] = None,
) -> str:
    """Create a new task for the user.

    Args:
        user_id: The authenticated user's ID.
        title: Task title (max 200 characters).
        description: Optional task description (max 2000 characters).
        priority: Optional priority level: "high", "medium", or "low".
        due_date: Optional due date in ISO format (YYYY-MM-DD).

    Returns:
        JSON string with the created task details.
    """
    with Session(engine) as session:
        task = Task(
            user_id=user_id,
            title=title[:200],
            description=description[:2000] if description else None,
            priority=PriorityEnum(priority) if priority else None,
            due_date=(
                date.fromisoformat(due_date) if due_date else None
            ),
        )
        session.add(task)
        session.commit()
        session.refresh(task)

        return json.dumps({
            "task_id": task.id,
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
            "priority": task.priority.value if task.priority else None,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "created_at": task.created_at.isoformat(),
        })


@mcp_server.tool()
def list_tasks(
    user_id: str,
    status: Optional[str] = None,
    priority: Optional[str] = None,
) -> str:
    """List tasks for the user with optional filters.

    Args:
        user_id: The authenticated user's ID.
        status: Optional filter: "pending" or "completed".
        priority: Optional filter: "high", "medium", or "low".

    Returns:
        JSON string with tasks array and count.
    """
    with Session(engine) as session:
        statement = select(Task).where(Task.user_id == user_id)

        if status == "pending":
            statement = statement.where(Task.completed == False)  # noqa: E712
        elif status == "completed":
            statement = statement.where(Task.completed == True)  # noqa: E712

        if priority:
            statement = statement.where(
                Task.priority == PriorityEnum(priority)
            )

        statement = statement.order_by(Task.created_at.desc())
        tasks = session.exec(statement).all()

        tasks_list = [
            {
                "task_id": t.id,
                "title": t.title,
                "description": t.description,
                "completed": t.completed,
                "priority": t.priority.value if t.priority else None,
                "due_date": t.due_date.isoformat() if t.due_date else None,
                "created_at": t.created_at.isoformat(),
            }
            for t in tasks
        ]

        return json.dumps({
            "tasks": tasks_list,
            "count": len(tasks_list),
        })


@mcp_server.tool()
def complete_task(user_id: str, task_id: str) -> str:
    """Mark a task as completed.

    Args:
        user_id: The authenticated user's ID.
        task_id: UUID of the task to complete.

    Returns:
        JSON string with updated task details, or error if not found.
    """
    with Session(engine) as session:
        task = session.exec(
            select(Task).where(
                Task.id == task_id, Task.user_id == user_id
            )
        ).first()

        if not task:
            return json.dumps({"error": "Task not found"})

        task.completed = True
        task.updated_at = datetime.utcnow()
        session.add(task)
        session.commit()
        session.refresh(task)

        return json.dumps({
            "task_id": task.id,
            "title": task.title,
            "completed": task.completed,
            "priority": task.priority.value if task.priority else None,
            "updated_at": task.updated_at.isoformat(),
        })


@mcp_server.tool()
def delete_task(user_id: str, task_id: str) -> str:
    """Permanently delete a task.

    Args:
        user_id: The authenticated user's ID.
        task_id: UUID of the task to delete.

    Returns:
        JSON string with deletion confirmation, or error if not found.
    """
    with Session(engine) as session:
        task = session.exec(
            select(Task).where(
                Task.id == task_id, Task.user_id == user_id
            )
        ).first()

        if not task:
            return json.dumps({"error": "Task not found"})

        title = task.title
        task_id_str = task.id
        session.delete(task)
        session.commit()

        return json.dumps({
            "deleted": True,
            "task_id": task_id_str,
            "title": title,
        })


@mcp_server.tool()
def update_task(
    user_id: str,
    task_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    due_date: Optional[str] = None,
) -> str:
    """Update one or more fields of an existing task.

    Args:
        user_id: The authenticated user's ID.
        task_id: UUID of the task to update.
        title: New title (optional).
        description: New description (optional).
        priority: New priority: "high", "medium", "low", or "none" to clear.
        due_date: New due date (ISO format) or "none" to clear.

    Returns:
        JSON string with updated task details, or error if not found.
    """
    with Session(engine) as session:
        task = session.exec(
            select(Task).where(
                Task.id == task_id, Task.user_id == user_id
            )
        ).first()

        if not task:
            return json.dumps({"error": "Task not found"})

        if title is not None:
            task.title = title[:200]
        if description is not None:
            task.description = description[:2000] if description else None
        if priority is not None:
            if priority.lower() == "none":
                task.priority = None
            else:
                task.priority = PriorityEnum(priority)
        if due_date is not None:
            if due_date.lower() == "none":
                task.due_date = None
            else:
                task.due_date = date.fromisoformat(due_date)

        task.updated_at = datetime.utcnow()
        session.add(task)
        session.commit()
        session.refresh(task)

        return json.dumps({
            "task_id": task.id,
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
            "priority": task.priority.value if task.priority else None,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "updated_at": task.updated_at.isoformat(),
        })
