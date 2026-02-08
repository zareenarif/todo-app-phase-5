"""
OpenAI Agents SDK chat agent for todo task management.

The agent:
- Receives natural language messages
- Maps intent to tool invocations (in-process function tools)
- Returns conversational responses
- Does NOT access the database directly
- Does NOT contain business logic

Uses Groq's free OpenAI-compatible API as the LLM provider.
"""
import json
from typing import Optional
from dataclasses import dataclass, field
from openai import AsyncOpenAI
from agents import Agent, Runner, OpenAIChatCompletionsModel, function_tool
from src.core.config import settings
from src.mcp.tools import add_task, list_tasks, complete_task, delete_task, update_task


SYSTEM_PROMPT = """You are a helpful todo task management assistant. You help users manage their tasks through natural language conversation.

## Available Tools
You have access to these task management tools:
- add_task: Create a new task
- list_tasks: List tasks with optional filters
- complete_task: Mark a task as completed
- delete_task: Permanently delete a task
- update_task: Update task fields (title, description, priority, due_date)

## Behavior Rules

### Tool Invocation
- When users want to create a task: use add_task
- When users want to see tasks: use list_tasks
- When users want to mark a task done: use complete_task (first use list_tasks to find the task_id if needed)
- When users want to remove a task: use delete_task (ALWAYS confirm before deleting)
- When users want to change a task: use update_task

### Confirmation Rules
- CREATE: No confirmation needed. Create immediately and confirm.
- COMPLETE: No confirmation needed. Mark complete and confirm.
- UPDATE: No confirmation needed. Apply changes and confirm.
- DELETE: ALWAYS ask for confirmation before deleting. Say "Are you sure you want to delete '[task title]'?" and wait for user to confirm.
- BULK OPERATIONS: ALWAYS confirm before any operation affecting multiple tasks.

### Error Handling
- If a task is not found: Say "I couldn't find that task. Want me to list your tasks?"
- If the reference is ambiguous: Say "I found multiple tasks matching that. Which one?" and list the matches.
- If a required field is missing: Ask for it specifically.
- If no tasks exist: Say "You don't have any tasks yet. Want to add one?"

### Important Rules
- You MUST ONLY help with task management. If a user asks about anything else (weather, math, general knowledge), politely say: "I can only help with task management. Would you like to add, list, update, complete, or delete tasks?"
- When referencing tasks, ALWAYS use list_tasks to look up task IDs. NEVER guess task IDs.
- Use conversation history to resolve references like "that one", "it", "the first one".
- Keep responses concise and friendly.
- Always include the task title in confirmations.

### The user_id Parameter
- For ALL tool calls, you MUST pass the user_id that is provided in the conversation context.
- The user_id will be provided as the first system message.
"""


# --- Agent-compatible function tools wrapping MCP tools ---

@function_tool(strict_mode=False)
def agent_add_task(
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
        description: Optional task description.
        priority: Optional priority level: "high", "medium", or "low".
        due_date: Optional due date in ISO format (YYYY-MM-DD).
    """
    return add_task(user_id, title, description, priority, due_date)


@function_tool(strict_mode=False)
def agent_list_tasks(
    user_id: str,
    status: Optional[str] = None,
    priority: Optional[str] = None,
) -> str:
    """List tasks for the user with optional filters.

    Args:
        user_id: The authenticated user's ID.
        status: Optional filter: "pending" or "completed".
        priority: Optional filter: "high", "medium", or "low".
    """
    return list_tasks(user_id, status, priority)


@function_tool(strict_mode=False)
def agent_complete_task(user_id: str, task_id: str) -> str:
    """Mark a task as completed.

    Args:
        user_id: The authenticated user's ID.
        task_id: UUID of the task to complete.
    """
    return complete_task(user_id, task_id)


@function_tool(strict_mode=False)
def agent_delete_task(user_id: str, task_id: str) -> str:
    """Permanently delete a task.

    Args:
        user_id: The authenticated user's ID.
        task_id: UUID of the task to delete.
    """
    return delete_task(user_id, task_id)


@function_tool(strict_mode=False)
def agent_update_task(
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
    """
    return update_task(user_id, task_id, title, description, priority, due_date)


TOOLS = [
    agent_add_task,
    agent_list_tasks,
    agent_complete_task,
    agent_delete_task,
    agent_update_task,
]


@dataclass
class AgentResult:
    """Result from running the chat agent."""
    response: str
    tool_calls: list = field(default_factory=list)


def format_messages_for_agent(
    user_id: str,
    messages: list,
) -> list:
    """Convert database Message records to OpenAI message format.

    Ensures strict alternation of user/assistant roles to satisfy
    Groq/OpenAI API requirements. Consecutive same-role messages
    are merged.

    Args:
        user_id: The authenticated user's ID (injected as system context).
        messages: List of Message model instances from database.

    Returns:
        List of dicts with 'role' and 'content' keys.
    """
    # Inject user_id as a user→assistant exchange to avoid consecutive user messages
    formatted = [
        {
            "role": "user",
            "content": f"My user_id is: {user_id}. Use this user_id for ALL tool calls.",
        },
        {
            "role": "assistant",
            "content": f"Understood. I will use user_id '{user_id}' for all tool calls.",
        },
    ]

    for msg in messages:
        if msg.role in ("user", "assistant"):
            content = msg.content or ""
            # Merge consecutive same-role messages to satisfy Groq's strict alternation
            if formatted and formatted[-1]["role"] == msg.role:
                formatted[-1]["content"] += "\n" + content
            else:
                formatted.append({
                    "role": msg.role,
                    "content": content,
                })

    # Ensure the last message before the new one isn't a user message
    # (the new user message will be appended by run_chat_agent)
    if formatted and formatted[-1]["role"] == "user":
        formatted.append({
            "role": "assistant",
            "content": "How can I help you with your tasks?",
        })

    return formatted


async def run_chat_agent(
    user_id: str,
    messages: list,
    new_message: str,
) -> AgentResult:
    """Run the chat agent with conversation history and a new message.

    Args:
        user_id: The authenticated user's ID.
        messages: Previous Message model instances from database.
        new_message: The new user message to process.

    Returns:
        AgentResult with response text and tool call records.
    """
    # Format conversation history
    history = format_messages_for_agent(user_id, messages)

    # Add the new user message
    history.append({"role": "user", "content": new_message})

    # Create Groq-backed OpenAI-compatible client (free tier)
    groq_client = AsyncOpenAI(
        api_key=settings.GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1",
    )
    groq_model = OpenAIChatCompletionsModel(
        model=settings.GROQ_MODEL,
        openai_client=groq_client,
    )

    # Create agent with function tools and Groq model
    agent = Agent(
        name="todo-assistant",
        instructions=SYSTEM_PROMPT,
        tools=TOOLS,
        model=groq_model,
    )

    # Run agent
    result = await Runner.run(
        agent,
        input=history,
    )

    # Extract response and tool calls
    response_text = result.final_output or ""
    tool_calls = []

    # Parse tool calls from the run result
    for item in result.new_items:
        if hasattr(item, "raw_item"):
            raw = item.raw_item
            # Check for tool call outputs
            if hasattr(raw, "type") and raw.type == "function_call_output":
                tool_calls.append({
                    "tool_name": getattr(item, "tool_name", "unknown"),
                    "tool_input": {},
                    "tool_output": raw.output if hasattr(raw, "output") else None,
                })
            # Check for function calls
            elif hasattr(raw, "type") and raw.type == "function_call":
                tool_calls.append({
                    "tool_name": raw.name if hasattr(raw, "name") else "unknown",
                    "tool_input": (
                        json.loads(raw.arguments)
                        if hasattr(raw, "arguments") and raw.arguments
                        else {}
                    ),
                    "tool_output": None,
                })

    # Merge function calls with their outputs
    merged_calls = []
    i = 0
    while i < len(tool_calls):
        call = tool_calls[i].copy()
        # If next item is an output for this call, merge them
        if (
            i + 1 < len(tool_calls)
            and tool_calls[i + 1].get("tool_output") is not None
            and tool_calls[i].get("tool_output") is None
        ):
            call["tool_output"] = tool_calls[i + 1]["tool_output"]
            i += 2
        else:
            i += 1
        if call.get("tool_name") != "unknown":
            merged_calls.append(call)

    return AgentResult(
        response=response_text,
        tool_calls=merged_calls,
    )
