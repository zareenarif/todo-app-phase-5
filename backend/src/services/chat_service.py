"""
Chat service — stateless flow orchestrator.

Handles conversation persistence and coordinates the chat agent.
Does NOT contain business logic — delegates to the agent + MCP tools.
"""
from datetime import datetime
from typing import Optional, List
from sqlmodel import Session, select
from src.core.database import engine
from src.models.conversation import Conversation, Message
from src.agents.chat_agent import run_chat_agent, AgentResult
from src.schemas.chat import ChatResponse, ToolCallRecord


def load_or_create_conversation(
    user_id: str,
    conversation_id: Optional[str],
) -> Conversation:
    """Load an existing conversation or create a new one.

    Args:
        user_id: The authenticated user's ID.
        conversation_id: Optional existing conversation ID.

    Returns:
        Conversation record (existing or newly created).

    Raises:
        ValueError: If conversation_id is provided but not found or wrong user.
    """
    with Session(engine) as session:
        if conversation_id:
            conversation = session.exec(
                select(Conversation).where(
                    Conversation.id == conversation_id,
                    Conversation.user_id == user_id,
                )
            ).first()

            if not conversation:
                raise ValueError("Conversation not found")

            return conversation

        # Create new conversation
        conversation = Conversation(user_id=user_id)
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
        return conversation


def load_messages(conversation_id: str) -> List[Message]:
    """Load all messages for a conversation ordered by created_at ascending.

    Args:
        conversation_id: The conversation's ID.

    Returns:
        List of Message records ordered chronologically.
    """
    with Session(engine) as session:
        messages = session.exec(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
        ).all()
        return list(messages)


def save_message(
    conversation_id: str,
    role: str,
    content: Optional[str] = None,
    tool_name: Optional[str] = None,
    tool_input: Optional[dict] = None,
    tool_output=None,
) -> Message:
    """Persist a single message record.

    Args:
        conversation_id: The conversation this message belongs to.
        role: Message role — "user", "assistant", or "tool".
        content: Text content (for user/assistant messages).
        tool_name: MCP tool name (for tool messages).
        tool_input: Tool input parameters (for tool messages).
        tool_output: Tool output result (for tool messages).

    Returns:
        The persisted Message record.
    """
    with Session(engine) as session:
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            tool_name=tool_name,
            tool_input=tool_input,
            tool_output=tool_output,
        )
        session.add(message)
        session.commit()
        session.refresh(message)
        return message


async def process_chat(
    user_id: str,
    conversation_id: Optional[str],
    message: str,
) -> ChatResponse:
    """Orchestrate the full stateless chat flow.

    Steps:
    1. Load or create conversation
    2. Load existing messages
    3. Save user message
    4. Run agent with conversation history + new message
    5. Save assistant response and tool call messages
    6. Return ChatResponse

    Args:
        user_id: The authenticated user's ID.
        conversation_id: Optional existing conversation ID.
        message: The new user message.

    Returns:
        ChatResponse with conversation_id, response, and tool_calls.

    Raises:
        ValueError: If conversation not found or wrong user.
    """
    # 1. Load or create conversation
    conversation = load_or_create_conversation(user_id, conversation_id)

    # 2. Load existing messages
    history = load_messages(conversation.id)

    # 3. Save user message
    save_message(
        conversation_id=conversation.id,
        role="user",
        content=message,
    )

    # 4. Run agent
    agent_result: AgentResult = await run_chat_agent(
        user_id=user_id,
        messages=history,
        new_message=message,
    )

    # 5. Save tool call messages
    for tool_call in agent_result.tool_calls:
        save_message(
            conversation_id=conversation.id,
            role="tool",
            tool_name=tool_call.get("tool_name"),
            tool_input=tool_call.get("tool_input"),
            tool_output=tool_call.get("tool_output"),
        )

    # Save assistant response
    save_message(
        conversation_id=conversation.id,
        role="assistant",
        content=agent_result.response,
    )

    # 6. Update conversation title from first message if new
    if not conversation.title and message:
        with Session(engine) as session:
            conv = session.get(Conversation, conversation.id)
            if conv:
                conv.title = message[:200]
                conv.updated_at = datetime.utcnow()
                session.add(conv)
                session.commit()

    # 7. Build response
    tool_call_records = [
        ToolCallRecord(
            tool_name=tc.get("tool_name", "unknown"),
            tool_input=tc.get("tool_input", {}),
            tool_output=tc.get("tool_output"),
        )
        for tc in agent_result.tool_calls
    ]

    return ChatResponse(
        conversation_id=conversation.id,
        response=agent_result.response,
        tool_calls=tool_call_records,
    )
