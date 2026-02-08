# MCP Tool Contracts

## Tool: add_task

**Input Schema:**
```json
{
  "user_id": "string (required)",
  "title": "string (required, max 200)",
  "description": "string (optional, max 2000)",
  "priority": "string (optional, enum: high|medium|low)",
  "due_date": "string (optional, ISO date YYYY-MM-DD)"
}
```

**Output Schema:**
```json
{
  "task_id": "string (UUID)",
  "title": "string",
  "description": "string|null",
  "completed": false,
  "priority": "string|null",
  "due_date": "string|null",
  "created_at": "string (ISO datetime)"
}
```

---

## Tool: list_tasks

**Input Schema:**
```json
{
  "user_id": "string (required)",
  "status": "string (optional, enum: pending|completed)",
  "priority": "string (optional, enum: high|medium|low)"
}
```

**Output Schema:**
```json
{
  "tasks": [
    {
      "task_id": "string",
      "title": "string",
      "description": "string|null",
      "completed": "boolean",
      "priority": "string|null",
      "due_date": "string|null",
      "created_at": "string"
    }
  ],
  "count": "integer"
}
```

---

## Tool: complete_task

**Input Schema:**
```json
{
  "user_id": "string (required)",
  "task_id": "string (required, UUID)"
}
```

**Output Schema:**
```json
{
  "task_id": "string",
  "title": "string",
  "completed": true,
  "priority": "string|null",
  "updated_at": "string (ISO datetime)"
}
```

**Error:** `{"error": "Task not found"}` if task_id invalid or wrong user

---

## Tool: delete_task

**Input Schema:**
```json
{
  "user_id": "string (required)",
  "task_id": "string (required, UUID)"
}
```

**Output Schema:**
```json
{
  "deleted": true,
  "task_id": "string",
  "title": "string"
}
```

**Error:** `{"error": "Task not found"}` if task_id invalid or wrong user

---

## Tool: update_task

**Input Schema:**
```json
{
  "user_id": "string (required)",
  "task_id": "string (required, UUID)",
  "title": "string (optional)",
  "description": "string (optional)",
  "priority": "string (optional, enum: high|medium|low|null)",
  "due_date": "string (optional, ISO date or null)"
}
```

**Output Schema:**
```json
{
  "task_id": "string",
  "title": "string",
  "description": "string|null",
  "completed": "boolean",
  "priority": "string|null",
  "due_date": "string|null",
  "updated_at": "string (ISO datetime)"
}
```

**Error:** `{"error": "Task not found"}` if task_id invalid or wrong user

---

## Statelessness Contract

All tools:
- MUST NOT maintain in-memory state between calls
- MUST create a fresh database session per invocation
- MUST filter by `user_id` on every query
- MUST return structured JSON (not free text)
