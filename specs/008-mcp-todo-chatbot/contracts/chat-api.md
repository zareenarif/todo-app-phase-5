# API Contract: Chat Endpoint

## POST /api/{user_id}/chat

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | String | Yes | Authenticated user ID (must match JWT) |

### Request Body

```json
{
  "conversation_id": "string (UUID, optional)",
  "message": "string (required, 1-10000 chars)"
}
```

### Response 200

```json
{
  "conversation_id": "string (UUID)",
  "response": "string",
  "tool_calls": [
    {
      "tool_name": "string",
      "tool_input": {},
      "tool_output": {}
    }
  ]
}
```

### Error Responses

| Status | Body |
|--------|------|
| 400 | `{"detail": "Message is required"}` |
| 401 | `{"detail": "Unauthorized"}` |
| 404 | `{"detail": "Conversation not found"}` |
| 500 | `{"detail": "Internal server error"}` |

### Authentication

- `Authorization: Bearer <jwt_token>` header required
- Path `user_id` MUST match JWT user_id
