# Research: AI-Powered Todo Chatbot (MCP Architecture)

**Feature**: 008-mcp-todo-chatbot
**Date**: 2026-02-08
**Status**: Complete

---

## R1: OpenAI Agents SDK Integration with MCP

**Decision:** Use OpenAI Agents SDK with MCP server tools registered
as function tools via the `mcp` parameter on the Agent class.

**Rationale:** The OpenAI Agents SDK natively supports MCP servers.
An Agent can be configured with `mcp_servers=[mcp_server]` which
auto-discovers and registers all MCP tools. The Runner executes the
agent loop, handling tool calls and responses automatically.

**Alternatives considered:**
- Manual function tools on Agent — rejected because MCP SDK provides
  structured tool registration with schema validation
- LangChain MCP adapter — rejected because constitution mandates
  OpenAI Agents SDK specifically

**Key integration pattern:**
- Create MCP server using `mcp.server.FastMCP`
- Register tools on the MCP server with `@mcp_server.tool()`
- Pass MCP server to Agent via `mcp_servers` parameter
- Use `Runner.run()` to execute the agent with conversation history
- Runner automatically handles tool call → MCP execution → response

---

## R2: MCP SDK for Python (Stateless Tool Server)

**Decision:** Use the official `mcp` Python SDK (`FastMCP` class) to
create an in-process MCP server with stateless tool functions.

**Rationale:** FastMCP provides decorator-based tool registration
(`@server.tool()`), automatic schema generation from type hints, and
in-process transport (no separate process needed). Each tool function
receives parameters, executes a database query via SQLModel, and
returns structured results.

**Alternatives considered:**
- Stdio transport MCP server — rejected because it requires a
  separate process; in-process is simpler for single-backend
- Custom tool registration — rejected because MCP SDK handles schema
  generation and validation

**Statelessness enforcement:**
- Tool functions MUST NOT use module-level state
- Tool functions MUST create fresh database sessions per invocation
- Tool functions MUST NOT cache results

---

## R3: Conversation State Management

**Decision:** Store messages as individual rows in a `messages` table
with foreign key to `conversations` table. Reconstruct history by
querying messages ordered by `created_at`.

**Rationale:** Row-per-message allows efficient querying, indexing,
and avoids JSON column size limits. Messages include role, content,
and tool call metadata for full reconstruction of agent context.

**Alternatives considered:**
- JSON array column on Conversation — rejected because it becomes
  unwieldy for long conversations and prevents individual message
  queries
- Separate tool_calls table — rejected because tool call data is
  small and can be stored as JSON fields on the message row

---

## R4: Existing Codebase Reuse

**Decision:** Extend the existing Phase 2 backend rather than
building from scratch. Reuse models, auth, database, and middleware.

**Rationale:** The existing backend has User model, Task model, JWT
auth, database configuration, CORS middleware, and error handling
already built and tested. Phase 3 adds new models (Conversation,
Message), new endpoints (chat), and new components (MCP server,
Agent) without modifying existing working code.

**What to reuse:**
- `backend/src/core/config.py` — extend with OPENAI_API_KEY
- `backend/src/core/database.py` — existing engine/session
- `backend/src/core/security.py` — JWT verification
- `backend/src/api/deps.py` — get_current_user dependency
- `backend/src/models/task.py` — existing Task model
- `backend/src/models/user.py` — existing User model
- `backend/src/middleware/` — CORS and error handling

**What to add:**
- `backend/src/models/conversation.py` — Conversation + Message
- `backend/src/mcp/` — MCP server and tool definitions
- `backend/src/agents/chat_agent.py` — OpenAI Agents SDK agent
- `backend/src/api/v1/chat.py` — Chat endpoint
- `frontend/` — ChatKit integration (minimal)

---

## R5: Authentication for Chat Endpoint

**Decision:** Reuse existing JWT-based auth. The `user_id` is
extracted from the JWT in the path parameter or via the existing
`get_current_user` dependency.

**Rationale:** The spec defines `POST /api/{user_id}/chat` with
`user_id` in the URL path. The existing auth system already verifies
JWTs and extracts user_id. We can validate that the path `user_id`
matches the JWT's `user_id` to prevent impersonation.

**Alternatives considered:**
- Remove user_id from path, use only JWT — viable but spec mandates
  `/api/{user_id}/chat` endpoint format
- Session-based auth — rejected per constitution (stateless mandate)

---

## R6: OpenAI ChatKit Frontend

**Decision:** Use OpenAI ChatKit React component connected to the
FastAPI chat endpoint. Minimal frontend — only chat UI.

**Rationale:** ChatKit provides a ready-made chat interface. The
frontend sends messages to `POST /api/{user_id}/chat` and displays
responses. No business logic in frontend per constitution.

**Key considerations:**
- ChatKit manages its own UI state (message display, input)
- Frontend stores `conversation_id` from responses for continuity
- Frontend includes auth token in request headers
- No task filtering, sorting, or management UI — all via chat

---

## R7: New Dependencies Required

**Decision:** Add the following Python packages:

| Package | Purpose |
|---------|---------|
| `openai-agents` | OpenAI Agents SDK for agent/runner |
| `mcp` | Official MCP SDK for tool server |
| `openai` | OpenAI API client (required by agents SDK) |

**Frontend packages:**
| Package | Purpose |
|---------|---------|
| `@openai/chatkit` | ChatKit React component |

**Rationale:** Minimum viable dependencies per constitution
(simplicity principle). Only add what the spec mandates.

**What to remove/not use:**
- `groq` — replaced by OpenAI for agent logic
- `apscheduler` — no background jobs (non-goal)
- Ollama fallback — not in spec, OpenAI is the mandated provider
