# Data Model: Cloud-Native Event-Driven Todo AI Chatbot

**Branch**: `010-cloud-native-deployment` | **Date**: 2026-02-09

## Existing Entities (Preserved)

### Task

**Table**: `tasks` (unchanged from Phase 3)

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | VARCHAR(36) | PK, UUID | Auto-generated |
| user_id | VARCHAR(36) | FK → users.id, NOT NULL, INDEX | Data isolation |
| title | VARCHAR(200) | NOT NULL | Required |
| description | VARCHAR(2000) | NULLABLE | Optional |
| completed | BOOLEAN | NOT NULL, DEFAULT FALSE | Completion status |
| priority | ENUM(high, medium, low) | NULLABLE | Optional priority |
| tags | JSON | NOT NULL, DEFAULT [] | Array of strings |
| due_date | DATE | NULLABLE | Optional deadline |
| recurrence | ENUM(daily, weekly, monthly) | NULLABLE | Recurrence pattern |
| created_at | DATETIME | NOT NULL | Auto-set |
| updated_at | DATETIME | NOT NULL | Auto-updated |

**No schema changes required.** All fields needed for Phase 5 (priority, tags, due_date, recurrence) already exist.

### User

**Table**: `users` (unchanged)

| Field | Type | Constraints |
|-------|------|-------------|
| id | VARCHAR(36) | PK |
| email | VARCHAR | NOT NULL, UNIQUE |
| name | VARCHAR | NULLABLE |
| password_hash | VARCHAR | NOT NULL |
| created_at | DATETIME | NOT NULL |
| updated_at | DATETIME | NOT NULL |

### Conversation / Message

**Tables**: `conversations`, `messages` (unchanged from Phase 3)

No changes. Conversation persistence is preserved.

### AgentLog / AgentMessage

**Tables**: `agent_logs`, `agent_messages` (unchanged from Phase 3)

No changes.

## New Entities

### Reminder

**Table**: `reminders` (NEW)

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | VARCHAR(36) | PK, UUID | Auto-generated |
| user_id | VARCHAR(36) | FK → users.id, NOT NULL, INDEX | Data isolation |
| task_id | VARCHAR(36) | FK → tasks.id, NOT NULL, INDEX | Associated task |
| remind_at | DATETIME | NOT NULL | When to fire reminder |
| lead_time | VARCHAR(10) | NOT NULL | "15min", "30min", "1h", "1d" |
| status | ENUM(pending, triggered, cancelled) | NOT NULL, DEFAULT pending | Lifecycle state |
| created_at | DATETIME | NOT NULL | Auto-set |
| updated_at | DATETIME | NOT NULL | Auto-updated |

**Validation rules**:
- `remind_at` MUST be before the associated task's `due_date`
- `task_id` MUST reference an existing task owned by `user_id`
- Only one active reminder per task (unique constraint on `task_id` WHERE `status = 'pending'`)

**State transitions**:
```
PENDING → TRIGGERED  (when remind_at time arrives and task is still active)
PENDING → CANCELLED  (when task is completed/deleted before remind_at)
```

### AuditLogEntry

**Table**: `audit_log` (NEW)

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | VARCHAR(36) | PK, UUID | Auto-generated |
| event_id | VARCHAR(36) | NOT NULL, UNIQUE | Deduplication key |
| event_type | VARCHAR(50) | NOT NULL | e.g., "task.created" |
| user_id | VARCHAR(36) | NOT NULL, INDEX | Who performed the action |
| task_id | VARCHAR(36) | NULLABLE | Which task was affected |
| timestamp | DATETIME | NOT NULL | When the event occurred |
| payload | JSON | NOT NULL | Full event data |
| created_at | DATETIME | NOT NULL | When the log entry was written |

**Constraints**:
- Append-only: no UPDATE or DELETE operations permitted
- `event_id` UNIQUE constraint ensures idempotent processing
- INDEX on `user_id` + `timestamp` for efficient querying

## Logical Entities (Not Persisted in DB)

### TaskEvent (Kafka Event Envelope)

Exists only on Kafka topics. Follows CloudEvents-compatible format.

| Field | Type | Notes |
|-------|------|-------|
| id | string (UUID) | Unique event identifier |
| source | string | "todo-backend" |
| type | string | "task.created", "task.updated", "task.completed", "task.deleted" |
| time | string (ISO 8601) | Event timestamp |
| data | object | Event-specific payload (task snapshot) |

### ReminderEvent (Kafka Event Envelope)

| Field | Type | Notes |
|-------|------|-------|
| id | string (UUID) | Unique event identifier |
| source | string | "todo-reminder-scheduler" |
| type | string | "reminder.triggered" |
| time | string (ISO 8601) | When the reminder fired |
| data | object | `{reminder_id, task_id, user_id, task_title, due_date}` |

## Entity Relationships

```
User (1) ──── (N) Task
User (1) ──── (N) Reminder
User (1) ──── (N) AuditLogEntry (via user_id)
Task (1) ──── (0..1) Reminder (one active reminder per task)
Task (1) ──── (N) AuditLogEntry (via task_id, multiple events per task)
```

## Migration Plan

**New Alembic migration**: `add_reminder_and_audit_tables`

1. Create `reminders` table with all columns and constraints
2. Create `audit_log` table with all columns and constraints
3. Add foreign key from `reminders.task_id` → `tasks.id` (CASCADE DELETE)
4. Add foreign key from `reminders.user_id` → `users.id`
5. Add unique index on `audit_log.event_id`
6. Add composite index on `audit_log(user_id, timestamp)`
