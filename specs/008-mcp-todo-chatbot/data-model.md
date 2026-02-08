# Data Model: AI-Powered Todo Chatbot (MCP Architecture)

**Feature**: 008-mcp-todo-chatbot
**Date**: 2026-02-08

---

## Entities

### Task (existing — no changes)

Reuse existing `backend/src/models/task.py`. No schema changes.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `id` | String (UUID) | PK, auto-generated | Existing |
| `user_id` | String | FK → users.id, indexed, NOT NULL | Existing |
| `title` | String(200) | NOT NULL | Existing |
| `description` | String(2000) | Nullable | Existing |
| `completed` | Boolean | Default: False | Existing |
| `priority` | Enum(high,medium,low) | Nullable | Existing |
| `tags` | JSON (List[str]) | Default: [] | Existing (not used in Phase 3 MCP tools) |
| `due_date` | Date | Nullable | Existing |
| `recurrence` | Enum(daily,weekly,monthly) | Nullable | Existing (not used in Phase 3 MCP tools) |
| `created_at` | DateTime | Auto, default NOW() | Existing |
| `updated_at` | DateTime | Auto-updated | Existing |

### User (existing — no changes)

Reuse existing `backend/src/models/user.py`. No schema changes.

| Field | Type | Constraints |
|-------|------|-------------|
| `id` | String | PK |
| `email` | String | Unique, indexed |
| `name` | String | Nullable |
| `password_hash` | String | NOT NULL |
| `created_at` | DateTime | Auto |
| `updated_at` | DateTime | Auto |

### Conversation (NEW)

**File:** `backend/src/models/conversation.py`

| Field | Type | Constraints |
|-------|------|-------------|
| `id` | String (UUID) | PK, auto-generated |
| `user_id` | String | FK → users.id, indexed, NOT NULL |
| `title` | String(200) | Nullable, auto-generated from first message |
| `created_at` | DateTime | Auto, default NOW() |
| `updated_at` | DateTime | Auto-updated |

**Indexes:** `user_id` (for listing user's conversations)

### Message (NEW)

**File:** `backend/src/models/conversation.py` (same file)

| Field | Type | Constraints |
|-------|------|-------------|
| `id` | String (UUID) | PK, auto-generated |
| `conversation_id` | String (UUID) | FK → conversations.id, indexed, NOT NULL |
| `role` | String | NOT NULL, one of: "user", "assistant", "tool" |
| `content` | Text | Nullable (required for user/assistant) |
| `tool_name` | String(100) | Nullable (required when role="tool") |
| `tool_input` | JSON | Nullable |
| `tool_output` | JSON | Nullable |
| `created_at` | DateTime | Auto, default NOW() |

**Indexes:**
- `conversation_id` (for loading conversation messages)
- `(conversation_id, created_at)` composite (for ordered retrieval)

---

## Relationships

```
User (1) ──── (*) Task
User (1) ──── (*) Conversation
Conversation (1) ──── (*) Message
```

- Deleting a Conversation cascades to its Messages
- User deletion policy: not in scope (no account deletion feature)

---

## Migration Required

**New Alembic migration** to create:
1. `conversations` table
2. `messages` table
3. Foreign key constraints
4. Indexes

No changes to existing `users` or `tasks` tables.

---

## Validation Rules

### Conversation
- `user_id` MUST match authenticated user
- `title` auto-generated: first 50 chars of first user message

### Message
- `content` MUST be non-empty when role is "user" or "assistant"
- `tool_name` MUST be non-empty when role is "tool"
- `role` MUST be one of: "user", "assistant", "tool"
- Messages ordered by `created_at` ascending within a conversation
