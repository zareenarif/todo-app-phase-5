"""
Chat API endpoints.

- POST /chat/{user_id}                          — Send a message
- GET  /chat/{user_id}/conversations             — List conversations
- GET  /chat/{user_id}/conversations/{conv_id}   — Get conversation messages
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, func
from src.api.deps import get_current_user
from src.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ConversationSummary,
    ConversationDetail,
    MessageRecord,
)
from src.services.chat_service import process_chat
from src.core.database import engine
from src.models.conversation import Conversation, Message

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/{user_id}", response_model=ChatResponse)
async def chat(
    user_id: str,
    request: ChatRequest,
    current_user_id: str = Depends(get_current_user),
):
    """Process a chat message through the AI agent.

    - Validates that path user_id matches JWT user_id
    - Delegates to chat service for stateless flow orchestration
    - Returns conversation_id, response, and tool_calls
    """
    # Validate user_id matches JWT
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )

    try:
        response = await process_chat(
            user_id=user_id,
            conversation_id=request.conversation_id,
            message=request.message,
        )
        return response
    except ValueError as e:
        # Conversation not found or wrong user
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except RuntimeError as e:
        # LLM provider errors (Groq rate limit, API failures)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI service temporarily unavailable. Please try again. ({e})",
        )
    except Exception as e:
        import logging
        logging.getLogger(__name__).error("Chat endpoint error: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get(
    "/{user_id}/conversations",
    response_model=List[ConversationSummary],
)
async def list_conversations(
    user_id: str,
    current_user_id: str = Depends(get_current_user),
):
    """List all conversations for the authenticated user."""
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )

    with Session(engine) as session:
        conversations = session.exec(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
        ).all()

        results = []
        for conv in conversations:
            count = session.exec(
                select(func.count())
                .select_from(Message)
                .where(Message.conversation_id == conv.id)
            ).one()
            results.append(
                ConversationSummary(
                    id=conv.id,
                    title=conv.title,
                    created_at=conv.created_at.isoformat(),
                    updated_at=conv.updated_at.isoformat(),
                    message_count=count,
                )
            )

        return results


@router.get(
    "/{user_id}/conversations/{conversation_id}",
    response_model=ConversationDetail,
)
async def get_conversation(
    user_id: str,
    conversation_id: str,
    current_user_id: str = Depends(get_current_user),
):
    """Get a conversation with all its messages."""
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )

    with Session(engine) as session:
        conversation = session.exec(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id,
            )
        ).first()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )

        messages = session.exec(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
        ).all()

        return ConversationDetail(
            id=conversation.id,
            title=conversation.title,
            created_at=conversation.created_at.isoformat(),
            updated_at=conversation.updated_at.isoformat(),
            messages=[
                MessageRecord(
                    id=m.id,
                    role=m.role,
                    content=m.content,
                    tool_name=m.tool_name,
                    tool_input=m.tool_input,
                    tool_output=m.tool_output,
                    created_at=m.created_at.isoformat(),
                )
                for m in messages
            ],
        )
