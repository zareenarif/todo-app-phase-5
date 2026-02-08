"""
Chat API endpoint — POST /api/{user_id}/chat.

Validates auth, delegates to chat service, returns ChatResponse.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from src.api.deps import get_current_user
from src.schemas.chat import ChatRequest, ChatResponse
from src.services.chat_service import process_chat

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
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
