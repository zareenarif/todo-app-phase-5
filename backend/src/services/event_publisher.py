"""
Event Publisher Service — Publishes domain events to Kafka via Dapr Pub/Sub.

All Kafka interaction is abstracted via the Dapr sidecar HTTP API.
No Kafka client SDK is used in application code (Constitution Principle XIV).

Dapr Sidecar API:
  POST http://localhost:{DAPR_HTTP_PORT}/v1.0/publish/{pubsub-name}/{topic}

The publisher is fire-and-forget: database writes are NEVER blocked by
event publishing failures. Dapr resiliency policy handles retries.
"""

from __future__ import annotations

import logging
import os
from typing import Optional

import httpx
from pydantic import BaseModel

from src.events.schemas import (
    TOPIC_TASK_EVENTS,
    TOPIC_TASK_UPDATES,
    TOPIC_REMINDERS,
    EventEnvelope,
    TaskCreatedData,
    TaskCompletedData,
    TaskDeletedData,
    TaskUpdatedData,
    ReminderTriggeredData,
    TaskEventType,
    create_task_event,
    create_task_update_event,
    create_reminder_event,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Dapr sidecar configuration (injected via ConfigMap)
# ---------------------------------------------------------------------------
DAPR_HTTP_PORT = int(os.getenv("DAPR_HTTP_PORT", "3500"))
DAPR_PUBSUB_NAME = os.getenv("DAPR_PUBSUB_NAME", "pubsub-kafka")
DAPR_BASE_URL = f"http://localhost:{DAPR_HTTP_PORT}"

# Dapr publish endpoint template
# POST /v1.0/publish/{pubsubname}/{topic}
_PUBLISH_URL = f"{DAPR_BASE_URL}/v1.0/publish/{DAPR_PUBSUB_NAME}"


class EventPublisherService:
    """
    Publishes domain events to Kafka topics via Dapr Pub/Sub sidecar.

    Usage:
        publisher = EventPublisherService()
        await publisher.publish_task_created(task, user_id)
        await publisher.publish_task_completed(task, user_id)
        await publisher.publish_task_deleted(task_id, user_id, title)
        await publisher.publish_task_updated(task_id, user_id, changes)

    All methods are fire-and-forget. Exceptions are logged but never raised
    to the caller — the database write MUST succeed independently of event
    publishing.
    """

    def __init__(self) -> None:
        self._client = httpx.AsyncClient(timeout=5.0)

    async def _publish(self, topic: str, envelope: EventEnvelope) -> bool:
        """
        Publish an event envelope to a Kafka topic via Dapr sidecar.

        Returns True if published successfully, False if failed.
        Failures are logged but never raised.
        """
        url = f"{_PUBLISH_URL}/{topic}"
        payload = envelope.model_dump()

        try:
            response = await self._client.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
            )
            if response.status_code in (200, 204):
                logger.info(
                    "Event published: topic=%s type=%s id=%s",
                    topic,
                    envelope.type,
                    envelope.id,
                )
                return True
            else:
                logger.warning(
                    "Event publish non-200: topic=%s status=%d body=%s",
                    topic,
                    response.status_code,
                    response.text[:200],
                )
                return False
        except httpx.HTTPError as exc:
            logger.error(
                "Event publish failed: topic=%s type=%s error=%s",
                topic,
                envelope.type,
                str(exc),
            )
            return False

    # ----- Task Lifecycle Events → todo.task-events -----

    async def publish_task_created(self, task, user_id: str) -> bool:
        """Publish task.created event after a new task is persisted."""
        data = TaskCreatedData(
            task_id=str(task.id),
            user_id=str(user_id),
            title=task.title,
            description=task.description,
            priority=task.priority.value if task.priority else None,
            tags=task.tags or [],
            due_date=task.due_date.isoformat() if task.due_date else None,
            recurrence=task.recurrence.value if task.recurrence else None,
            created_at=task.created_at.isoformat(),
        )
        envelope = create_task_event(TaskEventType.CREATED, data)
        return await self._publish(TOPIC_TASK_EVENTS, envelope)

    async def publish_task_completed(self, task, user_id: str) -> bool:
        """Publish task.completed event after a task is marked completed."""
        data = TaskCompletedData(
            task_id=str(task.id),
            user_id=str(user_id),
            title=task.title,
            recurrence=task.recurrence.value if task.recurrence else None,
            due_date=task.due_date.isoformat() if task.due_date else None,
            completed_at=task.updated_at.isoformat(),
        )
        envelope = create_task_event(TaskEventType.COMPLETED, data)
        return await self._publish(TOPIC_TASK_EVENTS, envelope)

    async def publish_task_deleted(
        self, task_id: str, user_id: str, title: str
    ) -> bool:
        """Publish task.deleted event after a task is removed."""
        from datetime import datetime

        data = TaskDeletedData(
            task_id=str(task_id),
            user_id=str(user_id),
            title=title,
            deleted_at=datetime.utcnow().isoformat(),
        )
        envelope = create_task_event(TaskEventType.DELETED, data)
        return await self._publish(TOPIC_TASK_EVENTS, envelope)

    # ----- Task Update Events → todo.task-updates -----

    async def publish_task_updated(
        self, task_id: str, user_id: str, changes: dict
    ) -> bool:
        """Publish task.updated event after task fields are modified."""
        from datetime import datetime

        data = TaskUpdatedData(
            task_id=str(task_id),
            user_id=str(user_id),
            changes=changes,
            updated_at=datetime.utcnow().isoformat(),
        )
        envelope = create_task_update_event(data)
        return await self._publish(TOPIC_TASK_UPDATES, envelope)

    # ----- Reminder Events → todo.reminders -----

    async def publish_reminder_triggered(
        self,
        reminder_id: str,
        task_id: str,
        user_id: str,
        task_title: str,
        due_date: Optional[str] = None,
    ) -> bool:
        """Publish reminder.triggered event when a scheduled reminder fires."""
        data = ReminderTriggeredData(
            reminder_id=str(reminder_id),
            task_id=str(task_id),
            user_id=str(user_id),
            task_title=task_title,
            due_date=due_date,
        )
        envelope = create_reminder_event(data)
        return await self._publish(TOPIC_REMINDERS, envelope)

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()


# ---------------------------------------------------------------------------
# Singleton instance
# ---------------------------------------------------------------------------
_publisher: Optional[EventPublisherService] = None


def get_event_publisher() -> EventPublisherService:
    """Get or create the singleton EventPublisherService."""
    global _publisher
    if _publisher is None:
        _publisher = EventPublisherService()
    return _publisher
