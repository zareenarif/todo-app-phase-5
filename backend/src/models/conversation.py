"""
Conversation and Message data models for chat persistence.
"""
from sqlmodel import Field, SQLModel, Column, Relationship
from sqlalchemy import String, Text, JSON, ForeignKey, Index
from datetime import datetime
from uuid import uuid4
from typing import Optional, Any, List


def generate_uuid() -> str:
    """Generate a UUID string."""
    return str(uuid4())


class Conversation(SQLModel, table=True):
    """
    Conversation entity representing a chat session.

    Each conversation belongs to a single user and contains
    an ordered sequence of messages.
    """
    __tablename__ = "conversations"

    id: str = Field(
        default_factory=generate_uuid,
        sa_column=Column(String(36), primary_key=True)
    )
    user_id: str = Field(
        sa_column=Column(
            String(36), ForeignKey("users.id"), nullable=False, index=True
        )
    )
    title: Optional[str] = Field(default=None, max_length=200)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )


class Message(SQLModel, table=True):
    """
    Message entity representing a single message in a conversation.

    Messages can be from the user, the assistant, or a tool invocation.
    Tool messages include tool_name, tool_input, and tool_output.
    """
    __tablename__ = "messages"
    __table_args__ = (
        Index("ix_messages_conversation_created", "conversation_id", "created_at"),
    )

    id: str = Field(
        default_factory=generate_uuid,
        sa_column=Column(String(36), primary_key=True)
    )
    conversation_id: str = Field(
        sa_column=Column(
            String(36),
            ForeignKey("conversations.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        )
    )
    role: str = Field(
        sa_column=Column(String(20), nullable=False)
    )
    content: Optional[str] = Field(
        default=None,
        sa_column=Column(Text, nullable=True)
    )
    tool_name: Optional[str] = Field(default=None, max_length=100)
    tool_input: Optional[Any] = Field(
        default=None,
        sa_column=Column(JSON, nullable=True)
    )
    tool_output: Optional[Any] = Field(
        default=None,
        sa_column=Column(JSON, nullable=True)
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )
