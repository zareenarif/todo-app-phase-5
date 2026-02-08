"""
Chat request and response schemas for the chat API endpoint.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Any


class ChatRequest(BaseModel):
    """Request body for POST /api/{user_id}/chat."""
    conversation_id: Optional[str] = Field(
        default=None,
        description="Existing conversation ID. If omitted, creates new conversation.",
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="User's natural language message.",
    )


class ToolCallRecord(BaseModel):
    """Record of a single MCP tool invocation."""
    tool_name: str = Field(description="Name of the MCP tool invoked")
    tool_input: dict = Field(
        default_factory=dict,
        description="Parameters passed to the tool",
    )
    tool_output: Any = Field(
        default=None,
        description="Result returned by the tool",
    )


class ChatResponse(BaseModel):
    """Response body for POST /api/{user_id}/chat."""
    conversation_id: str = Field(
        description="The conversation ID (new or existing)"
    )
    response: str = Field(
        description="Agent's natural language response"
    )
    tool_calls: List[ToolCallRecord] = Field(
        default_factory=list,
        description="List of MCP tool invocations made during this request",
    )
