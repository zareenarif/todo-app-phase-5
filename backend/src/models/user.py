"""
User reference model.
Note: User table is managed by Better Auth.
This model is for reference only (foreign key relationships).
"""
from sqlmodel import SQLModel, Field, Column
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from datetime import datetime
from uuid import UUID
from typing import Optional


class User(SQLModel, table=True):
    """
    User entity with authentication.

    Attributes:
        id: Unique user identifier (UUID)
        email: User's email address (unique)
        name: User's display name (optional)
        password_hash: Hashed password for authentication
        created_at: Account creation timestamp
        updated_at: Last update timestamp
    """
    __tablename__ = "users"

    id: UUID = Field(
        sa_column=Column(PGUUID(as_uuid=True), primary_key=True)
    )
    email: str = Field(unique=True, index=True)
    name: Optional[str] = Field(default=None)
    password_hash: str
    created_at: datetime
    updated_at: datetime
