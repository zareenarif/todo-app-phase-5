"""
Dapr Subscription Event Handlers — receives events delivered by Dapr sidecar.

Dapr subscriptions (defined in dapr-subscription.yaml) route Kafka topic messages
to these FastAPI endpoints. The sidecar delivers events via HTTP POST.

Routes:
  POST /events/task-events     ← todo.task-events (audit, recurrence, reminder suppression)
  POST /events/task-updates    ← todo.task-updates (audit)
  POST /events/reminders       ← todo.reminders (reminder status update)
  POST /job/{job_name}         ← Dapr Jobs API callback (reminder trigger)
  GET  /dapr/subscribe         ← Programmatic subscription discovery (fallback)

All handlers are idempotent. Duplicate events produce no duplicate side effects.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["events"])


# =========================================================================
# Dapr Programmatic Subscription Discovery (fallback)
# =========================================================================
# If declarative subscriptions (dapr-subscription.yaml) are not deployed,
# Dapr falls back to asking the app via GET /dapr/subscribe.

@router.get("/dapr/subscribe")
async def dapr_subscribe():
    """
    Return programmatic subscription list for Dapr.

    Dapr calls this on app startup to discover subscriptions.
    Only used if declarative Subscription CRDs are not deployed.
    """
    return [
        {
            "pubsubname": "pubsub-kafka",
            "topic": "todo.task-events",
            "route": "/events/task-events",
            "deadLetterTopic": "todo.task-events.dlq",
        },
        {
            "pubsubname": "pubsub-kafka",
            "topic": "todo.task-updates",
            "route": "/events/task-updates",
            "deadLetterTopic": "todo.task-updates.dlq",
        },
        {
            "pubsubname": "pubsub-kafka",
            "topic": "todo.reminders",
            "route": "/events/reminders",
            "deadLetterTopic": "todo.reminders.dlq",
        },
    ]


# =========================================================================
# Handler: todo.task-events
# =========================================================================
# Consumers: AuditService, RecurrenceService, ReminderSuppression

@router.post("/events/task-events")
async def handle_task_events(request: Request) -> JSONResponse:
    """
    Handle events from the todo.task-events Kafka topic.

    Event types:
      - task.created   → AuditService logs entry
      - task.completed → AuditService logs + RecurrenceService generates next task
                         + ReminderSuppression cancels pending reminders
      - task.deleted   → AuditService logs + ReminderSuppression cancels

    Dapr expects one of:
      {"status": "SUCCESS"}  → event processed, ACK
      {"status": "RETRY"}    → event should be retried
      {"status": "DROP"}     → event dropped (do not retry)
    """
    try:
        event = await request.json()
        event_type = event.get("type", "unknown")
        event_id = event.get("id", "unknown")
        data = event.get("data", {})

        logger.info(
            "Received task event: type=%s id=%s task_id=%s",
            event_type,
            event_id,
            data.get("task_id"),
        )

        # --- Audit logging (all event types) ---
        await _handle_audit_log(event)

        # --- Recurrence handling (task.completed only) ---
        if event_type == "task.completed":
            await _handle_recurrence(event)
            await _handle_reminder_suppression(data.get("task_id"))

        # --- Reminder suppression (task.deleted) ---
        if event_type == "task.deleted":
            await _handle_reminder_suppression(data.get("task_id"))

        return JSONResponse(content={"status": "SUCCESS"})

    except Exception as exc:
        logger.error("Task event handler error: %s", exc, exc_info=True)
        return JSONResponse(content={"status": "RETRY"})


# =========================================================================
# Handler: todo.task-updates
# =========================================================================
# Consumers: AuditService

@router.post("/events/task-updates")
async def handle_task_updates(request: Request) -> JSONResponse:
    """
    Handle events from the todo.task-updates Kafka topic.

    Event types:
      - task.updated → AuditService logs entry

    Separated from task-events to allow independent scaling and retention.
    """
    try:
        event = await request.json()
        event_id = event.get("id", "unknown")
        data = event.get("data", {})

        logger.info(
            "Received task update event: id=%s task_id=%s",
            event_id,
            data.get("task_id"),
        )

        # Audit logging
        await _handle_audit_log(event)

        return JSONResponse(content={"status": "SUCCESS"})

    except Exception as exc:
        logger.error("Task update handler error: %s", exc, exc_info=True)
        return JSONResponse(content={"status": "RETRY"})


# =========================================================================
# Handler: todo.reminders
# =========================================================================
# Consumers: ReminderService

@router.post("/events/reminders")
async def handle_reminders(request: Request) -> JSONResponse:
    """
    Handle events from the todo.reminders Kafka topic.

    Event types:
      - reminder.triggered → Update reminder status, suppress if task inactive

    Published by Dapr Jobs API when a scheduled reminder fires.
    """
    try:
        event = await request.json()
        event_id = event.get("id", "unknown")
        data = event.get("data", {})

        logger.info(
            "Received reminder event: id=%s reminder_id=%s task_id=%s",
            event_id,
            data.get("reminder_id"),
            data.get("task_id"),
        )

        await _handle_reminder_triggered(data)

        return JSONResponse(content={"status": "SUCCESS"})

    except Exception as exc:
        logger.error("Reminder handler error: %s", exc, exc_info=True)
        return JSONResponse(content={"status": "RETRY"})


# =========================================================================
# Handler: Dapr Jobs API Callback
# =========================================================================

@router.post("/job/{job_name}")
async def handle_job_callback(job_name: str, request: Request) -> JSONResponse:
    """
    Handle Dapr Jobs API callback when a scheduled job fires.

    URL: POST /job/{job_name}

    For reminder jobs (name pattern: "reminder-{reminder_id}"):
      1. Load reminder from database
      2. Check if task is still active
      3. If active: publish reminder.triggered event to todo.reminders
      4. If inactive: cancel reminder (status → CANCELLED)
    """
    try:
        payload = await request.json()
        logger.info("Job fired: name=%s", job_name)

        if job_name.startswith("reminder-"):
            reminder_id = job_name.replace("reminder-", "")
            await _handle_reminder_job_fired(reminder_id, payload)
        else:
            logger.warning("Unknown job type: name=%s", job_name)

        return JSONResponse(content={"status": "SUCCESS"})

    except Exception as exc:
        logger.error("Job callback error: name=%s error=%s", job_name, exc, exc_info=True)
        return JSONResponse(content={"status": "RETRY"})


# =========================================================================
# Internal Handler Functions
# =========================================================================

async def _handle_audit_log(event: dict[str, Any]) -> None:
    """
    Write an audit log entry for any task event.

    Idempotent: checks event_id uniqueness before INSERT.
    Delegates to AuditService (will be wired in /sp.implement phase).
    """
    from src.services.audit_service import get_audit_service

    audit_service = get_audit_service()
    await audit_service.log_event(event)


async def _handle_recurrence(event: dict[str, Any]) -> None:
    """
    Generate next task instance if the completed task has a recurrence pattern.

    Only invoked for task.completed events.
    Delegates to RecurrenceService.
    """
    from src.services.recurrence_service import get_recurrence_service

    data = event.get("data", {})
    recurrence = data.get("recurrence")

    if not recurrence:
        return  # Non-recurring task — nothing to do

    recurrence_service = get_recurrence_service()
    await recurrence_service.handle_task_completed(event)


async def _handle_reminder_suppression(task_id: str | None) -> None:
    """
    Cancel any pending reminders for a completed or deleted task.
    """
    if not task_id:
        return

    from src.services.reminder_service import get_reminder_service

    reminder_service = get_reminder_service()
    await reminder_service.suppress_by_task_id(task_id)


async def _handle_reminder_triggered(data: dict[str, Any]) -> None:
    """
    Process a reminder.triggered event — update reminder status.
    """
    from src.services.reminder_service import get_reminder_service

    reminder_service = get_reminder_service()
    await reminder_service.handle_reminder_triggered(
        reminder_id=data.get("reminder_id", ""),
        task_id=data.get("task_id", ""),
    )


async def _handle_reminder_job_fired(reminder_id: str, payload: dict) -> None:
    """
    Handle Dapr Jobs callback for a reminder.
    Publishes reminder.triggered event to todo.reminders topic.
    """
    from src.services.reminder_service import get_reminder_service

    reminder_service = get_reminder_service()
    await reminder_service.fire_reminder(reminder_id)
