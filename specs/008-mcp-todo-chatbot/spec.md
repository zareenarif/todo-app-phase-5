# Feature Specification: AI-Powered Todo Chatbot (MCP Architecture)

**Feature Branch**: `008-mcp-todo-chatbot`
**Created**: 2026-02-08
**Status**: Draft
**Input**: User description: "Build a conversational AI chatbot that manages todos using natural language via MCP tools"

---

## 1. Objective

Build an AI-powered conversational Todo chatbot where users manage
their tasks entirely through natural language. The system uses Model
Context Protocol (MCP) architecture: an AI agent (OpenAI Agents SDK)
interprets user messages and orchestrates task operations through
stateless MCP tools, with all state persisted in a Neon PostgreSQL
database.

**Key outcomes:**
- Users create, list, update, complete, and delete tasks via chat
- The AI agent translates natural language into MCP tool invocations
- All server components are stateless
- Conversation history is persisted in the database
- MCP tools are the exclusive interface between agent and task data

---

## 2. Architecture

### System Components

```
┌──────────────┐     ┌──────────────────────────────────────┐     ┌────────────┐
│  OpenAI      │     │         FastAPI Backend               │     │   Neon     │
│  ChatKit     │────>│                                      │────>│ PostgreSQL │
│  (Frontend)  │<────│  POST /api/{user_id}/chat            │<────│            │
└──────────────┘     │    |                                  │     └────────────┘
                     │    v                                  │
                     │  Load conversation from DB            │
                     │    |                                  │
                     │    v                                  │
                     │  Append user message                  │
                     │    |                                  │
                     │    v                                  │
                     │  ┌──────────────────────────┐        │
                     │  │ OpenAI Agents SDK         │        │
                     │  │ (Agent + Runner)          │        │
                     │  │   |                       │        │
                     │  │   v                       │        │
                     │  │ ┌──────────────────────┐  │        │
                     │  │ │ MCP Server            │  │        │
                     │  │ │ (Stateless Tools)     │──┼────────┼──> DB
                     │  │ └──────────────────────┘  │        │
                     │  └──────────────────────────┘        │
                     │    |                                  │
                     │    v                                  │
                     │  Persist messages to DB               │
                     │    |                                  │
                     │    v                                  │
                     │  Return response                      │
                     └──────────────────────────────────────┘
```

### Component Responsibilities

| Component | Technology | Responsibility |
|-----------|-----------|----------------|
| Frontend | OpenAI ChatKit | Render chat UI, send/receive messages |
| Backend API | Python FastAPI | Receive chat requests, orchestrate stateless flow |
| AI Agent | OpenAI Agents SDK | Interpret natural language, invoke MCP tools |
| MCP Server | Official MCP SDK | Expose stateless task operation tools |
| Database | Neon PostgreSQL + SQLModel | Persist tasks, conversations, messages |
| Auth | Better Auth | Authenticate users via stateless tokens |

### Architectural Invariants

- The FastAPI server MUST be stateless
- MCP tools MUST be stateless
- MCP tools MUST ONLY expose task operations
- The AI agent MUST use MCP tools for ALL task actions
- The AI agent MUST NOT access the database directly
- No business logic in the frontend
- Conversation state MUST be persisted in the database
- All task data MUST be isolated per user

---

## 3. Stateless Chat Flow

Every chat request follows this exact lifecycle. No server-side
memory is permitted at any step.

### Request Lifecycle

**Step 1 — Receive Request**
- FastAPI receives `POST /api/{user_id}/chat`
- Validate user authentication
- Extract `conversation_id` (optional) and `message` (required)

**Step 2 — Load Conversation from DB**
- If `conversation_id` provided: load existing conversation and its
  messages from the database
- If `conversation_id` not provided: create a new conversation record
- Reconstruct message history from persisted records

**Step 3 — Append User Message**
- Create a new message record: `role=user`, `content=<message>`
- Persist immediately to the database

**Step 4 — Run Agent with MCP Tools**
- Initialize OpenAI Agents SDK agent with MCP tool definitions
- Pass reconstructed conversation history as context
- Agent processes the user message and invokes MCP tools as needed
- Each MCP tool executes against the database and returns results
- Agent formulates a natural language response

**Step 5 — Persist Messages**
- Persist the assistant response as a message record:
  `role=assistant`, `content=<response>`
- If tool calls occurred, persist tool call records:
  `role=tool`, `tool_name=<name>`, `tool_input=<params>`,
  `tool_output=<result>`
- Update conversation `updated_at` timestamp

**Step 6 — Return Response**
- Return JSON response with `conversation_id`, `response` text,
  and `tool_calls` array
- Server releases all in-memory state — nothing is retained

### Statelessness Guarantee

- No in-memory conversation cache
- No server-side session storage
- No global state between requests
- Every request is self-contained: load -> process -> persist -> respond
- Server restart MUST NOT lose any data

---

## 4. Database Models (SQLModel)

### Task Model

| Field | Type | Constraints |
|-------|------|-------------|
| `id` | UUID | Primary key, auto-generated |
| `user_id` | String | Required, indexed, NOT NULL |
| `title` | String(200) | Required, NOT NULL |
| `description` | String(2000) | Optional, nullable |
| `completed` | Boolean | Default: False |
| `priority` | Enum('high','medium','low') | Optional, nullable |
| `due_date` | Date | Optional, nullable |
| `created_at` | DateTime | Auto-generated, default NOW() |
| `updated_at` | DateTime | Auto-updated on change |

### Conversation Model

| Field | Type | Constraints |
|-------|------|-------------|
| `id` | UUID | Primary key, auto-generated |
| `user_id` | String | Required, indexed, NOT NULL |
| `title` | String(200) | Optional, auto-generated from first message |
| `created_at` | DateTime | Auto-generated, default NOW() |
| `updated_at` | DateTime | Auto-updated on change |

### Message Model

| Field | Type | Constraints |
|-------|------|-------------|
| `id` | UUID | Primary key, auto-generated |
| `conversation_id` | UUID | Foreign key to Conversation.id, indexed |
| `role` | Enum('user','assistant','tool') | Required, NOT NULL |
| `content` | Text | Required for user/assistant roles |
| `tool_name` | String(100) | Required when role='tool' |
| `tool_input` | JSON | Tool call parameters, nullable |
| `tool_output` | JSON | Tool call result, nullable |
| `created_at` | DateTime | Auto-generated, default NOW() |

### Model Relationships

- A **User** has many **Tasks** (via `user_id`)
- A **User** has many **Conversations** (via `user_id`)
- A **Conversation** has many **Messages** (via `conversation_id`)
- Messages are ordered by `created_at` ascending

---

## 5. Chat API

### Endpoint: `POST /api/{user_id}/chat`

**Purpose:** Single endpoint for all conversational interactions.
The AI agent determines which MCP tools to invoke based on the
natural language message.

### Request

```json
{
  "conversation_id": "uuid-string-optional",
  "message": "Add a task to buy groceries with high priority"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `conversation_id` | String (UUID) | No | Existing conversation ID. If omitted, creates new conversation. |
| `message` | String | Yes | User's natural language message. MUST be non-empty. |

### Response

```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "response": "Done! I've added 'Buy groceries' with high priority to your tasks.",
  "tool_calls": [
    {
      "tool_name": "add_task",
      "tool_input": {
        "user_id": "user-123",
        "title": "Buy groceries",
        "priority": "high"
      },
      "tool_output": {
        "task_id": "a1b2c3d4-...",
        "title": "Buy groceries",
        "priority": "high",
        "completed": false
      }
    }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `conversation_id` | String (UUID) | The conversation ID (new or existing) |
| `response` | String | Agent's natural language response |
| `tool_calls` | Array | List of MCP tool invocations made during this request |

### Error Responses

| Status | Condition | Response |
|--------|-----------|----------|
| 400 | Empty or missing `message` | `{"detail": "Message is required"}` |
| 401 | Invalid or missing authentication | `{"detail": "Unauthorized"}` |
| 404 | `conversation_id` not found or not owned by user | `{"detail": "Conversation not found"}` |
| 500 | Agent or MCP tool failure | `{"detail": "Internal server error"}` |

---

## 6. MCP Server

### Responsibilities

The MCP server exposes task operations as stateless tools that the
AI agent can invoke. The MCP server:

- Registers tool definitions with the OpenAI Agents SDK
- Receives tool invocations from the agent
- Executes database operations via SQLModel
- Returns structured results to the agent
- Enforces user isolation on every operation

### Statelessness Contract

- MCP tools MUST NOT maintain any in-memory state
- MCP tools MUST NOT cache query results
- MCP tools MUST read from and write to the database on every call
- Each tool invocation is independent and self-contained
- The MCP server has no knowledge of conversation context

### Tool Registration

All tools MUST be registered with the MCP SDK and made available to
the OpenAI Agents SDK agent. Each tool MUST declare its name,
description, and input schema.

---

## 7. MCP Tools (Mandatory)

### 7.1 `add_task`

**Purpose:** Create a new task for the authenticated user.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | String | Yes | Authenticated user's ID |
| `title` | String | Yes | Task title (max 200 chars) |
| `description` | String | No | Task description (max 2000 chars) |
| `priority` | String | No | One of: "high", "medium", "low" |
| `due_date` | String | No | ISO date format: "YYYY-MM-DD" |

**Returns:** Created task object with all fields.

**Example Input:**
```json
{
  "user_id": "user-123",
  "title": "Buy groceries",
  "priority": "high",
  "due_date": "2026-02-10"
}
```

**Example Output:**
```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "title": "Buy groceries",
  "description": null,
  "completed": false,
  "priority": "high",
  "due_date": "2026-02-10",
  "created_at": "2026-02-08T14:30:00Z"
}
```

### 7.2 `list_tasks`

**Purpose:** List tasks for the authenticated user with optional
filters.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | String | Yes | Authenticated user's ID |
| `status` | String | No | Filter: "pending" or "completed" |
| `priority` | String | No | Filter: "high", "medium", or "low" |

**Returns:** Array of task objects matching filters.

**Example Input:**
```json
{
  "user_id": "user-123",
  "status": "pending"
}
```

**Example Output:**
```json
{
  "tasks": [
    {
      "task_id": "a1b2c3d4-...",
      "title": "Buy groceries",
      "completed": false,
      "priority": "high",
      "due_date": "2026-02-10"
    },
    {
      "task_id": "b2c3d4e5-...",
      "title": "Call dentist",
      "completed": false,
      "priority": "medium",
      "due_date": null
    }
  ],
  "count": 2
}
```

### 7.3 `complete_task`

**Purpose:** Mark a task as completed (or toggle completion status).

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | String | Yes | Authenticated user's ID |
| `task_id` | String | Yes | UUID of the task to complete |

**Returns:** Updated task object.

**Example Input:**
```json
{
  "user_id": "user-123",
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

**Example Output:**
```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "title": "Buy groceries",
  "completed": true,
  "priority": "high",
  "updated_at": "2026-02-08T15:00:00Z"
}
```

### 7.4 `delete_task`

**Purpose:** Permanently delete a task.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | String | Yes | Authenticated user's ID |
| `task_id` | String | Yes | UUID of the task to delete |

**Returns:** Confirmation with deleted task details.

**Example Input:**
```json
{
  "user_id": "user-123",
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

**Example Output:**
```json
{
  "deleted": true,
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "title": "Buy groceries"
}
```

### 7.5 `update_task`

**Purpose:** Update one or more fields of an existing task.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | String | Yes | Authenticated user's ID |
| `task_id` | String | Yes | UUID of the task to update |
| `title` | String | No | New title |
| `description` | String | No | New description |
| `priority` | String | No | New priority: "high", "medium", "low", or null |
| `due_date` | String | No | New due date (ISO format) or null to clear |

**Returns:** Updated task object with all fields.

**Example Input:**
```json
{
  "user_id": "user-123",
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "priority": "low",
  "due_date": "2026-02-15"
}
```

**Example Output:**
```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "title": "Buy groceries",
  "description": null,
  "completed": false,
  "priority": "low",
  "due_date": "2026-02-15",
  "updated_at": "2026-02-08T15:30:00Z"
}
```

---

## 8. Agent Behavior Rules

### 8.1 Tool Invocation Rules

The AI agent MUST invoke MCP tools according to these rules:

| User Intent | Required Tool | Trigger Phrases |
|------------|---------------|-----------------|
| Create a task | `add_task` | "add", "create", "new task", "remind me" |
| View tasks | `list_tasks` | "show", "list", "what are my tasks", "pending" |
| Mark complete | `complete_task` | "done", "complete", "finish", "mark as done" |
| Remove a task | `delete_task` | "delete", "remove", "cancel" |
| Modify a task | `update_task` | "change", "update", "rename", "set priority" |

### 8.2 Confirmation Rules

- **Create:** No confirmation needed. Create immediately and confirm.
- **Complete:** No confirmation needed. Mark complete and confirm.
- **Update:** No confirmation needed. Apply changes and confirm.
- **Delete:** Agent MUST confirm before deleting: "Are you sure you
  want to delete '[task title]'?" Execute only after user confirms.
- **Bulk operations:** Agent MUST confirm before any operation
  affecting multiple tasks.

### 8.3 Error Handling

| Error Condition | Agent Behavior |
|-----------------|---------------|
| Task not found | "I couldn't find that task. Want me to list your tasks?" |
| Ambiguous reference | "I found multiple tasks matching that. Which one?" + list matches |
| Missing required field | "I need a title for the task. What should it be called?" |
| Invalid priority value | "Priority must be high, medium, or low. Which would you like?" |
| Invalid date format | "I need a date like 2026-02-15. When is it due?" |
| MCP tool failure | "Something went wrong. Let me try that again." (retry once) |
| No tasks found | "You don't have any tasks yet. Want to add one?" |

### 8.4 Multi-Step Tool Chaining

The agent MUST handle operations requiring multiple tool calls:

**"Delete all completed tasks":**
1. Call `list_tasks` with `status=completed`
2. Ask user to confirm: "You have N completed tasks. Delete all?"
3. On confirmation: call `delete_task` for each task
4. Report: "Deleted N completed tasks."

**"What's my highest priority task?":**
1. Call `list_tasks` with `priority=high`, `status=pending`
2. If results: present the first/most relevant task
3. If no results: "You don't have any high priority tasks."

**"Complete 'buy groceries' and add 'pick up dry cleaning'":**
1. Call `list_tasks` to find "buy groceries"
2. Call `complete_task` on the matched task
3. Call `add_task` with title "pick up dry cleaning"
4. Report both actions completed

### 8.5 Conversation Context Rules

- The agent MUST use conversation history to resolve references
  (e.g., "mark that one as done" refers to the last discussed task)
- The agent MUST NOT hallucinate tasks that do not exist
- The agent MUST call `list_tasks` when it needs to look up task
  references rather than guessing IDs

---

## 9. Natural Language Mapping

### Primary Mapping Table

| User Phrase | Tool Call | Parameters Extracted |
|------------|-----------|---------------------|
| "Add a task to buy milk" | `add_task` | title="Buy milk" |
| "Create a high priority task: finish report" | `add_task` | title="Finish report", priority="high" |
| "Remind me to call dentist by Friday" | `add_task` | title="Call dentist", due_date=next Friday |
| "Show my tasks" | `list_tasks` | (no filters) |
| "List pending tasks" | `list_tasks` | status="pending" |
| "What are my high priority tasks?" | `list_tasks` | priority="high" |
| "Show completed tasks" | `list_tasks` | status="completed" |
| "Mark 'buy milk' as done" | `complete_task` | (lookup task by title match) |
| "I finished the report" | `complete_task` | (lookup task by title match) |
| "Delete the groceries task" | `delete_task` | (lookup + confirm) |
| "Remove all completed tasks" | `list_tasks` then `delete_task` x N | (multi-step) |
| "Change priority of 'call dentist' to high" | `update_task` | priority="high" |
| "Rename 'buy milk' to 'buy whole milk'" | `update_task` | title="Buy whole milk" |
| "Set due date for report to Feb 15" | `update_task` | due_date="2026-02-15" |
| "What do I need to do today?" | `list_tasks` | due_date=today |
| "How many tasks do I have?" | `list_tasks` | (count from response) |

### Ambiguity Resolution

| Ambiguous Input | Agent Behavior |
|----------------|---------------|
| "task" (alone) | "What would you like to do? I can add, list, update, complete, or delete tasks." |
| "delete it" (no context) | "Which task would you like to delete? Let me list your tasks." |
| "the important one" | Call `list_tasks` with priority="high" and present matches |
| "everything" | "Do you want to see all tasks, or do something to all of them?" |

---

## User Scenarios & Testing

### User Story 1 — Create Tasks via Chat (Priority: P1)

A user opens the chatbot and creates tasks using natural language.
The system correctly parses intent, invokes `add_task`, and confirms
the creation.

**Why this priority:** Task creation is the foundational capability.
Without it, no other features are meaningful.

**Independent Test:** Send "Add a task called 'buy groceries'" and
verify the task appears in the database with correct fields.

**Acceptance Scenarios:**

1. **Given** the user is authenticated, **When** they send "Add a
   task to buy groceries", **Then** `add_task` is invoked with
   title="Buy groceries" and the agent confirms creation.

2. **Given** the user is authenticated, **When** they send "Create
   a high priority task: finish report by 2026-02-15", **Then**
   `add_task` is invoked with title="Finish report",
   priority="high", due_date="2026-02-15".

3. **Given** the user sends an empty message, **Then** the API
   returns 400 with "Message is required".

---

### User Story 2 — List and Query Tasks (Priority: P1)

A user asks to see their tasks, optionally filtered by status or
priority. The system invokes `list_tasks` and presents results
conversationally.

**Why this priority:** Viewing tasks is equally fundamental — users
must see what they have created.

**Independent Test:** Create 3 tasks, then send "Show my tasks" and
verify all 3 are included in the response.

**Acceptance Scenarios:**

1. **Given** the user has 3 pending tasks, **When** they send "Show
   my tasks", **Then** `list_tasks` is invoked and the agent lists
   all 3 tasks.

2. **Given** the user has tasks with mixed priorities, **When** they
   send "Show high priority tasks", **Then** `list_tasks` is invoked
   with priority="high" and only matching tasks are shown.

3. **Given** the user has no tasks, **When** they send "List my
   tasks", **Then** the agent responds "You don't have any tasks
   yet. Want to add one?"

---

### User Story 3 — Complete Tasks via Chat (Priority: P1)

A user marks tasks as done using natural language. The system
resolves the task reference, invokes `complete_task`, and confirms.

**Why this priority:** Completing tasks is core to todo functionality.

**Independent Test:** Create a task, send "Mark 'buy groceries' as
done", verify the task's `completed` field is `true`.

**Acceptance Scenarios:**

1. **Given** a pending task titled "Buy groceries", **When** the user
   sends "Mark buy groceries as done", **Then** `complete_task` is
   invoked and the agent confirms completion.

2. **Given** no task matches the reference, **When** the user sends
   "Complete the shopping task", **Then** the agent responds that it
   could not find a matching task and offers to list tasks.

---

### User Story 4 — Update Tasks via Chat (Priority: P2)

A user modifies task properties using natural language. The system
invokes `update_task` with the appropriate field changes.

**Why this priority:** Important but secondary to create/list/complete.

**Independent Test:** Create a task, send "Change priority to high",
verify the task's priority field is updated.

**Acceptance Scenarios:**

1. **Given** a task "Buy groceries" with no priority, **When** the
   user sends "Set buy groceries to high priority", **Then**
   `update_task` is invoked with priority="high".

2. **Given** a task "Buy groceries", **When** the user sends "Rename
   it to buy organic groceries", **Then** `update_task` is invoked
   with title="Buy organic groceries".

---

### User Story 5 — Delete Tasks via Chat (Priority: P2)

A user deletes tasks using natural language. The system asks for
confirmation before executing the deletion.

**Why this priority:** Destructive operation, needs confirmation flow.

**Independent Test:** Create a task, send "Delete buy groceries",
confirm when asked, verify task is removed from database.

**Acceptance Scenarios:**

1. **Given** a task "Buy groceries", **When** the user sends "Delete
   buy groceries", **Then** the agent asks "Are you sure you want to
   delete 'Buy groceries'?" and waits for confirmation.

2. **Given** the agent has asked for delete confirmation, **When** the
   user responds "Yes", **Then** `delete_task` is invoked and the
   agent confirms deletion.

3. **Given** the agent has asked for delete confirmation, **When** the
   user responds "No", **Then** the deletion is cancelled and the
   agent confirms.

---

### User Story 6 — Conversation Persistence (Priority: P1)

A user's conversation history is preserved across requests. The
stateless server reconstructs context from the database on each
request.

**Why this priority:** Critical for stateless architecture compliance.

**Independent Test:** Send a message, note the conversation_id. Send
another message with the same conversation_id. Verify the agent has
context from the previous message.

**Acceptance Scenarios:**

1. **Given** a new user with no conversations, **When** they send a
   message without `conversation_id`, **Then** a new conversation is
   created and `conversation_id` is returned.

2. **Given** an existing conversation where the user added "Buy
   groceries", **When** the user sends "Mark that as done" in the
   same conversation, **Then** the agent resolves "that" to "Buy
   groceries" using persisted conversation history.

3. **Given** the server restarts between requests, **When** the user
   sends a follow-up message with their `conversation_id`, **Then**
   the agent has full context from prior messages.

---

### User Story 7 — Multi-User Isolation (Priority: P1)

Each user's tasks and conversations are isolated. Users MUST NOT
see or modify each other's data.

**Why this priority:** Security and data integrity requirement.

**Independent Test:** Create tasks for user A, then query as user B.
Verify user B sees no tasks.

**Acceptance Scenarios:**

1. **Given** user A has 3 tasks, **When** user B sends "Show my
   tasks", **Then** user B sees zero tasks (or only their own tasks).

2. **Given** user A's task ID is known, **When** user B sends
   "Complete [user A's task ID]", **Then** the agent responds "Task
   not found" (no information leakage).

---

### Edge Cases

- User sends only whitespace: 400 Bad Request
- User sends extremely long message (>10,000 chars): truncate or
  reject with helpful message
- User references a task by partial title match: agent finds best
  match or asks for clarification
- User sends non-task-related message ("What's the weather?"): agent
  politely redirects to task management
- Concurrent requests to same conversation: database serialization
  prevents corruption
- Invalid `conversation_id` format: 400 Bad Request
- `conversation_id` belongs to different user: 404 Not Found

---

## Requirements

### Functional Requirements

- **FR-001**: System MUST accept natural language messages and
  return natural language responses via a single chat endpoint
- **FR-002**: System MUST translate natural language into MCP tool
  invocations (add_task, list_tasks, complete_task, delete_task,
  update_task)
- **FR-003**: System MUST persist all conversation messages in the
  database
- **FR-004**: System MUST reconstruct conversation context from
  database on each request (stateless)
- **FR-005**: System MUST isolate all data by authenticated user_id
- **FR-006**: MCP tools MUST be stateless with no in-memory state
- **FR-007**: MCP tools MUST persist all changes to the database
- **FR-008**: System MUST confirm before destructive operations
  (delete)
- **FR-009**: System MUST handle ambiguous task references by asking
  for clarification
- **FR-010**: System MUST support multi-step tool chaining within
  a single request
- **FR-011**: System MUST return tool_calls array in the response
  for transparency and debugging
- **FR-012**: Agent MUST only respond to task-management requests
  and politely decline unrelated queries

### Key Entities

- **Task**: A todo item with title, description, priority, due date,
  completion status — owned by a single user
- **Conversation**: A chat session containing an ordered sequence of
  messages — owned by a single user
- **Message**: A single message within a conversation — can be from
  user, assistant, or tool invocation

---

## Success Criteria

### Measurable Outcomes

- **SC-001**: Users can create a task via natural language in a single
  message exchange
- **SC-002**: Users can list, complete, update, and delete tasks via
  natural language
- **SC-003**: Conversation context persists across multiple request
  cycles without server-side memory
- **SC-004**: Server restart does not lose any task or conversation
  data
- **SC-005**: Two different users cannot see or modify each other's
  tasks
- **SC-006**: The AI agent correctly maps at least 90% of the
  natural language phrases in the mapping table to the correct MCP
  tool
- **SC-007**: All MCP tool invocations are recorded in the
  `tool_calls` response field
- **SC-008**: Delete operations require explicit user confirmation
  before execution

---

## 10. Non-Goals

The following are explicitly NOT part of this specification:

- **No UI state management**: ChatKit handles all UI state. The
  backend has no knowledge of UI state.
- **No agent memory**: The AI agent has no persistent memory. All
  context comes from the database-loaded conversation history.
- **No business logic in frontend**: The ChatKit frontend sends
  messages and displays responses. No filtering, sorting, or task
  logic.
- **No background jobs**: No scheduled tasks, cron jobs, or
  asynchronous processing.
- **No real-time updates**: No WebSocket or SSE. Chat is
  request-response only.
- **No file uploads or attachments**: Tasks are text-only.
- **No task sharing or collaboration**: Tasks are strictly per-user.
- **No notification system**: No email, push, or in-app
  notifications.
- **No tags or recurrence**: Simplified from Phase 2 — only title,
  description, priority, due_date, and completed status.
- **No admin panel**: No user management or system administration.
- **No direct API for task CRUD**: All task operations go through
  the chat endpoint via MCP tools. No separate REST endpoints for
  tasks.

---

## Assumptions

- Better Auth is already configured from Phase 2 and provides
  `user_id` for authentication
- Neon PostgreSQL database is provisioned and accessible via
  `DATABASE_URL`
- OpenAI API key is available via `OPENAI_API_KEY` environment
  variable
- The MCP SDK supports in-process tool registration with the
  OpenAI Agents SDK
- ChatKit connects to the FastAPI backend's chat endpoint
