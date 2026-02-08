# Implementation Plan: AI-Powered Todo Chatbot (MCP Architecture)

**Branch**: `008-mcp-todo-chatbot` | **Date**: 2026-02-08 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/008-mcp-todo-chatbot/spec.md`

## Summary

Build an AI-powered conversational Todo chatbot using MCP architecture.
The system adds a chat endpoint to the existing FastAPI backend, with
an OpenAI Agents SDK agent orchestrating task operations through
stateless MCP tools. Conversation state is persisted in PostgreSQL.
The frontend uses OpenAI ChatKit for the chat interface.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript (frontend)
**Primary Dependencies**: FastAPI, OpenAI Agents SDK, MCP SDK, SQLModel, OpenAI ChatKit
**Storage**: Neon Serverless PostgreSQL (existing)
**Testing**: Manual testing per spec (automated optional)
**Target Platform**: Web (Linux server backend, browser frontend)
**Project Type**: Web application (frontend + backend)
**Performance Goals**: Standard web app response times
**Constraints**: Stateless server, stateless MCP tools, all state in DB
**Scale/Scope**: Single-user per request, conversation persistence

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| # | Principle | Status | Notes |
|---|-----------|--------|-------|
| I | Specification Before Implementation | PASS | spec.md approved |
| II | Planning Before Coding | PASS | This plan document |
| III | Tasks Before Execution | PENDING | tasks.md next step |
| IV | Simplicity Over Complexity | PASS | Using SDK defaults, thin MCP tools |
| V | Scope Discipline | PASS | Only spec'd features, no creep |
| VI | Security by Design | PASS | JWT auth, user isolation, input validation |
| VII | Stateless Server & MCP Tools | PASS | No in-memory state, DB persistence |
| VIII | MCP Tool Discipline | PASS | 5 tools, agent-only access via MCP |
| IX | Conversation State Persistence | PASS | Messages table, DB reconstruction |
| X | AI Agent Boundary Discipline | PASS | Agent uses Agents SDK, tools only |

**Gate result: PASS** — No violations. No complexity justification needed.

## Project Structure

### Documentation (this feature)

```text
specs/008-mcp-todo-chatbot/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   ├── chat-api.md      # Chat endpoint contract
│   └── mcp-tools.md     # MCP tool schemas
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2 output (/sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── core/
│   │   ├── config.py          # EXTEND: add OPENAI_API_KEY
│   │   ├── database.py        # REUSE: existing engine/session
│   │   └── security.py        # REUSE: JWT verification
│   ├── models/
│   │   ├── user.py            # REUSE: existing User model
│   │   ├── task.py            # REUSE: existing Task model
│   │   └── conversation.py    # NEW: Conversation + Message models
│   ├── schemas/
│   │   ├── task.py            # REUSE: existing schemas
│   │   └── chat.py            # NEW: ChatRequest + ChatResponse
│   ├── api/
│   │   ├── deps.py            # REUSE: get_current_user
│   │   └── v1/
│   │       ├── auth.py        # REUSE: existing auth
│   │       ├── tasks.py       # REUSE: existing CRUD
│   │       └── chat.py        # NEW: POST /api/{user_id}/chat
│   ├── mcp/
│   │   ├── __init__.py        # NEW: MCP package
│   │   ├── server.py          # NEW: FastMCP server setup
│   │   └── tools.py           # NEW: 5 MCP tool definitions
│   ├── agents/
│   │   └── chat_agent.py      # NEW: OpenAI Agents SDK agent
│   ├── services/
│   │   └── chat_service.py    # NEW: Stateless chat flow orchestrator
│   ├── middleware/             # REUSE: existing CORS + error handler
│   └── main.py                # EXTEND: register chat router
├── alembic/
│   └── versions/
│       └── xxx_add_conversation_tables.py  # NEW: migration
├── requirements.txt           # EXTEND: add openai-agents, mcp, openai
└── .env                       # EXTEND: add OPENAI_API_KEY

frontend/
├── src/
│   ├── app/
│   │   └── chat/
│   │       └── page.tsx       # NEW: ChatKit page
│   └── components/
│       └── ChatInterface.tsx  # NEW: ChatKit wrapper
├── package.json               # EXTEND: add @openai/chatkit
└── .env.local                 # EXTEND: add API URL
```

**Structure Decision**: Web application pattern (frontend + backend).
Extending existing Phase 2 backend with new MCP layer and chat
endpoint. Frontend adds minimal ChatKit integration page.

---

## Implementation Stages

### Stage 1: Database & Models

**Goal:** Create Conversation and Message database models and run
migration.

**Components involved:**
- `backend/src/models/conversation.py` — NEW
- `backend/alembic/versions/` — NEW migration
- `backend/src/core/config.py` — EXTEND

**Expected outcome:**
- Conversation and Message tables exist in PostgreSQL
- Models importable and usable with SQLModel sessions
- `OPENAI_API_KEY` added to Settings class
- Migration reversible (up and down)

---

### Stage 2: MCP Server & Tools

**Goal:** Create stateless MCP server with 5 task operation tools.

**Components involved:**
- `backend/src/mcp/server.py` — NEW (FastMCP instance)
- `backend/src/mcp/tools.py` — NEW (add_task, list_tasks,
  complete_task, delete_task, update_task)
- `backend/requirements.txt` — EXTEND (add `mcp`)

**Expected outcome:**
- MCP server with 5 registered tools
- Each tool receives parameters, queries DB via SQLModel, returns JSON
- All tools enforce user_id filtering
- All tools are stateless (fresh session per call)
- Tool schemas match contracts/mcp-tools.md

---

### Stage 3: AI Agent

**Goal:** Create OpenAI Agents SDK agent configured with MCP tools.

**Components involved:**
- `backend/src/agents/chat_agent.py` — NEW
- `backend/requirements.txt` — EXTEND (add `openai-agents`, `openai`)

**Expected outcome:**
- Agent created with system prompt for todo task management
- Agent connected to MCP server tools
- Agent receives conversation history and produces responses
- Agent maps natural language to MCP tool calls
- Agent asks for confirmation on delete operations
- Agent declines non-task-related queries

---

### Stage 4: Chat Service & API Endpoint

**Goal:** Create the stateless chat flow orchestrator and HTTP
endpoint.

**Components involved:**
- `backend/src/services/chat_service.py` — NEW
- `backend/src/schemas/chat.py` — NEW
- `backend/src/api/v1/chat.py` — NEW
- `backend/src/main.py` — EXTEND (register chat router)

**Expected outcome:**
- `POST /api/{user_id}/chat` endpoint operational
- Stateless flow: load conversation → append message → run agent →
  persist → return
- New conversations created when no conversation_id provided
- Existing conversations loaded and continued
- tool_calls array included in response
- Error handling per spec (400, 401, 404, 500)
- User isolation enforced (path user_id matches JWT)

---

### Stage 5: Frontend ChatKit Integration

**Goal:** Add minimal ChatKit frontend for conversational UI.

**Components involved:**
- `frontend/src/app/chat/page.tsx` — NEW
- `frontend/src/components/ChatInterface.tsx` — NEW
- `frontend/package.json` — EXTEND (add ChatKit dependency)
- `frontend/.env.local` — EXTEND (API URL)

**Expected outcome:**
- Chat page accessible at `/chat`
- ChatKit renders conversation interface
- Messages sent to backend chat endpoint
- Responses displayed in chat UI
- conversation_id managed for session continuity
- Auth token included in requests
- No business logic in frontend

---

### Stage 6: Integration & Validation

**Goal:** End-to-end testing of the complete flow.

**Components involved:**
- All components (frontend → backend → agent → MCP → DB)

**Expected outcome:**
- Full chat flow works: user types → agent responds → tasks created
- All 5 MCP tools invocable via natural language
- Conversation persistence verified across requests
- Server restart preserves all data (stateless verification)
- Multi-user isolation confirmed
- Delete confirmation flow works
- Error cases handled gracefully
- tool_calls visible in API responses

---

## Stage Dependencies

```
Stage 1 (DB/Models) ─── no dependencies
    │
    ├──> Stage 2 (MCP Tools) ─── depends on Stage 1 (needs DB models)
    │        │
    │        └──> Stage 3 (Agent) ─── depends on Stage 2 (needs MCP tools)
    │                 │
    │                 └──> Stage 4 (Chat API) ─── depends on Stage 3 (needs agent)
    │
    └──> Stage 5 (Frontend) ─── depends on Stage 4 (needs chat endpoint)
              │
              └──> Stage 6 (Integration) ─── depends on all stages
```

**Critical path:** Stage 1 → 2 → 3 → 4 → 5 → 6

**Parallel opportunities:**
- Stage 5 frontend skeleton can start alongside Stage 2-3 (mock API)
- Stage 2 MCP tools can be tested independently before agent

---

## Key Design Decisions

### D1: In-Process MCP Server

MCP server runs in-process with FastAPI (not as a separate service).
Tools are Python functions registered on a FastMCP instance, passed
to the Agent via `mcp_servers` parameter.

**Rationale:** Simplest architecture. No IPC overhead, no deployment
complexity. Constitution principle IV (simplicity).

### D2: Per-Request Agent Initialization

The agent is initialized fresh on each request with conversation
history loaded from the database. No persistent agent instances.

**Rationale:** Enforces statelessness (principle VII). Each request
is self-contained. Agent receives full context via messages.

### D3: Message-Per-Row Storage

Each message (user, assistant, tool) is stored as an individual
database row rather than a JSON array on the conversation.

**Rationale:** Better queryability, indexing, and no JSON size limits.
Aligns with relational database best practices.

### D4: Extend Existing Backend

New code is added alongside existing Phase 2 code. No existing
endpoints are modified or removed.

**Rationale:** Preserves working code, minimizes risk, and allows
incremental validation. Constitution principle IV (simplicity).

---

## Complexity Tracking

> No violations detected. All design decisions align with constitution.

| Check | Result |
|-------|--------|
| Stateless server | PASS — no in-memory state |
| Stateless MCP tools | PASS — fresh DB session per call |
| Agent boundary | PASS — agent uses MCP tools only |
| No frontend logic | PASS — ChatKit display only |
| Conversation persistence | PASS — messages table in DB |
| User isolation | PASS — user_id filter on all queries |

---

## Risks

1. **OpenAI Agents SDK + MCP compatibility**: The SDK's MCP
   integration is relatively new. If in-process MCP server doesn't
   work, fallback to stdio transport with subprocess.

2. **Agent response quality**: Natural language → tool mapping depends
   on the system prompt quality. May need iteration on the prompt.

3. **Conversation history length**: Long conversations may exceed
   token limits. Mitigation: truncate old messages, keeping most
   recent N messages.
