"""
Event Envelope Schemas — CloudEvents-compatible.

All events published to Kafka via Dapr Pub/Sub follow this envelope format.
Application code NEVER uses a Kafka SDK directly (Constitution Principle XIV).
All Kafka interaction is abstracted via Dapr sidecar HTTP API.

Topics:
  - todo.task-events: task.created, task.completed, task.deleted
  - todo.task-updates: task.updated
  - todo.reminders: reminder.triggered

Contracts: specs/010-cloud-native-deployment/contracts/task-events.yaml
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


# =============================================================================
# Event Type Enums
# =============================================================================

class TaskEventType(str, Enum):
    """Task lifecycle event types routed to todo.task-events."""
    CREATED = "task.created"
    COMPLETED = "task.completed"
    DELETED = "task.deleted"


class TaskUpdateEventType(str, Enum):
    """Task field update event type routed to todo.task-updates."""
    UPDATED = "task.updated"


class ReminderEventType(str, Enum):
    """Reminder event type routed to todo.reminders."""
    TRIGGERED = "reminder.triggered"


# =============================================================================
# Event Envelope (CloudEvents subset)
# =============================================================================

class EventEnvelope(BaseModel):
    """
    CloudEvents-compatible event envelope.
    Ref: https://cloudevents.io/

    Fields:
      id      — Unique event identifier (UUID, used for deduplication)
      source  — Producer identifier ("todo-backend" or "todo-reminder-scheduler")
      type    — Event type string (e.g. "task.created")
      time    — ISO 8601 timestamp of when the event occurred
      data    — Event-specific payload
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source: str
    type: str
    time: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    data: dict[str, Any]


# =============================================================================
# Task Event Data Payloads (match contracts/task-events.yaml)
# =============================================================================

class TaskCreatedData(BaseModel):
    """Payload for task.created events. Published to todo.task-events."""
    task_id: str
    user_id: str
    title: str
    description: Optional[str] = None
    priority: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    due_date: Optional[str] = None          # ISO date string
    recurrence: Optional[str] = None        # daily | weekly | monthly
    created_at: str


class TaskUpdatedData(BaseModel):
    """Payload for task.updated events. Published to todo.task-updates."""
    task_id: str
    user_id: str
    changes: dict[str, Any]                 # Changed fields with new values
    updated_at: str


class TaskCompletedData(BaseModel):
    """Payload for task.completed events. Published to todo.task-events."""
    task_id: str
    user_id: str
    title: str
    recurrence: Optional[str] = None
    due_date: Optional[str] = None
    completed_at: str


class TaskDeletedData(BaseModel):
    """Payload for task.deleted events. Published to todo.task-events."""
    task_id: str
    user_id: str
    title: str
    deleted_at: str


# =============================================================================
# Reminder Event Data Payload (match contracts/reminders-api.yaml)
# =============================================================================

class ReminderTriggeredData(BaseModel):
    """Payload for reminder.triggered events. Published to todo.reminders."""
    reminder_id: str
    task_id: str
    user_id: str
    task_title: str
    due_date: Optional[str] = None


# =============================================================================
# Topic Constants
# =============================================================================

TOPIC_TASK_EVENTS = "todo.task-events"
TOPIC_TASK_UPDATES = "todo.task-updates"
TOPIC_REMINDERS = "todo.reminders"

# Dead letter topics (routed automatically by Dapr resiliency policy)
TOPIC_TASK_EVENTS_DLQ = "todo.task-events.dlq"
TOPIC_TASK_UPDATES_DLQ = "todo.task-updates.dlq"
TOPIC_REMINDERS_DLQ = "todo.reminders.dlq"


# =============================================================================
# Factory Helpers
# =============================================================================

def create_task_event(event_type: TaskEventType, data: BaseModel) -> EventEnvelope:
    """Create a task event envelope for publishing to Kafka via Dapr."""
    return EventEnvelope(
        source="todo-backend",
        type=event_type.value,
        data=data.model_dump(),
    )


def create_task_update_event(data: TaskUpdatedData) -> EventEnvelope:
    """Create a task update event envelope for publishing to todo.task-updates."""
    return EventEnvelope(
        source="todo-backend",
        type=TaskUpdateEventType.UPDATED.value,
        data=data.model_dump(),
    )


def create_reminder_event(data: ReminderTriggeredData) -> EventEnvelope:
    """Create a reminder event envelope for publishing to todo.reminders."""
    return EventEnvelope(
        source="todo-reminder-scheduler",
        type=ReminderEventType.TRIGGERED.value,
        data=data.model_dump(),
    )
