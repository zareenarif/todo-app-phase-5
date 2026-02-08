# Tasks: AI-Powered Todo Chatbot (MCP Architecture)

**Input**: Design documents from `/specs/008-mcp-todo-chatbot/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Not explicitly requested — tests are OPTIONAL per spec.

**Organization**: Tasks follow the 6-stage plan, mapped to user stories for traceability.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US7)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: Install new dependencies and configure environment

- [x] T001 Add openai, openai-agents, and mcp packages to backend/requirements.txt
- [x] T002 [P] Add OPENAI_API_KEY setting to backend/src/core/config.py
- [x] T003 [P] Create backend/src/mcp/__init__.py package initializer

**Checkpoint**: Dependencies installed, config extended, MCP package exists

---

## Phase 2: Foundational (Database Models & Migration)

**Purpose**: Create Conversation and Message models and database tables. BLOCKS all user stories.

**CRITICAL**: No user story work can begin until this phase is complete.

- [x] T004 Create Conversation SQLModel in backend/src/models/conversation.py with fields: id (UUID PK), user_id (String FK indexed), title (String 200 nullable), created_at (DateTime auto), updated_at (DateTime auto)
- [x] T005 Create Message SQLModel in backend/src/models/conversation.py with fields: id (UUID PK), conversation_id (UUID FK indexed), role (String NOT NULL), content (Text nullable), tool_name (String 100 nullable), tool_input (JSON nullable), tool_output (JSON nullable), created_at (DateTime auto)
- [x] T006 Add composite index (conversation_id, created_at) on Message model for ordered retrieval
- [x] T007 Create Alembic migration for conversations and messages tables in backend/alembic/versions/
- [x] T008 Run migration and verify tables exist in database
- [x] T009 Create ChatRequest Pydantic schema in backend/src/schemas/chat.py with fields: conversation_id (Optional UUID), message (String required non-empty)
- [x] T010 [P] Create ChatResponse Pydantic schema in backend/src/schemas/chat.py with fields: conversation_id (String), response (String), tool_calls (List of ToolCallRecord)
- [x] T011 [P] Create ToolCallRecord Pydantic schema in backend/src/schemas/chat.py with fields: tool_name (String), tool_input (Dict), tool_output (Dict)

**Checkpoint**: Conversation and Message tables in DB. Chat schemas ready. Foundation complete.

---

## Phase 3: MCP Server & Tools — US1 Create + US2 List (Priority: P1)

**Goal**: Build the MCP server with add_task and list_tasks tools, enabling task creation and listing via MCP.

**Independent Test**: Call add_task tool directly with user_id and title, verify task in DB. Call list_tasks, verify results.

### Implementation

- [x] T012 Create FastMCP server instance in backend/src/mcp/server.py with server name and description
- [x] T013 Implement add_task MCP tool in backend/src/mcp/tools.py — receives user_id, title, description, priority, due_date; creates Task via SQLModel; returns task object JSON per contracts/mcp-tools.md
- [x] T014 Implement list_tasks MCP tool in backend/src/mcp/tools.py — receives user_id, status (optional), priority (optional); queries tasks filtered by user_id and optional filters; returns tasks array with count per contracts/mcp-tools.md
- [x] T015 Register add_task and list_tasks tools on the FastMCP server in backend/src/mcp/server.py
- [x] T016 Verify add_task tool creates task in database with correct user_id isolation
- [x] T017 Verify list_tasks tool returns only tasks for the given user_id

**Checkpoint**: add_task and list_tasks MCP tools work independently against database.

---

## Phase 4: MCP Tools — US3 Complete + US4 Update + US5 Delete (Priority: P1/P2)

**Goal**: Complete the MCP tool set with complete_task, update_task, and delete_task.

**Independent Test**: Call each tool directly, verify database state changes.

### Implementation

- [x] T018 [P] Implement complete_task MCP tool in backend/src/mcp/tools.py — receives user_id, task_id; toggles completed field; returns updated task per contracts/mcp-tools.md; returns error if task not found or wrong user
- [x] T019 [P] Implement update_task MCP tool in backend/src/mcp/tools.py — receives user_id, task_id, optional title/description/priority/due_date; updates specified fields; returns full task per contracts/mcp-tools.md; returns error if task not found
- [x] T020 [P] Implement delete_task MCP tool in backend/src/mcp/tools.py — receives user_id, task_id; deletes task; returns confirmation with task_id and title per contracts/mcp-tools.md; returns error if task not found
- [x] T021 Register complete_task, update_task, and delete_task on the FastMCP server in backend/src/mcp/server.py
- [x] T022 Verify all 5 MCP tools enforce user_id filtering (user A cannot access user B tasks)
- [x] T023 Verify all MCP tools are stateless — no module-level state, fresh DB session per call

**Checkpoint**: All 5 MCP tools operational. Statelessness verified. User isolation verified.

---

## Phase 5: AI Agent — US1-US5 Natural Language Mapping (Priority: P1)

**Goal**: Create OpenAI Agents SDK agent that maps natural language to MCP tool calls.

**Independent Test**: Initialize agent with conversation history, send "Add a task called buy groceries", verify add_task tool is invoked.

### Implementation

- [x] T024 Create chat agent module in backend/src/agents/chat_agent.py with function to create an Agent instance using OpenAI Agents SDK
- [x] T025 Write system prompt for the agent in backend/src/agents/chat_agent.py — define agent role as todo task manager, list available tools, specify behavior rules from spec section 8 (confirmation on delete, decline non-task queries, error handling phrases)
- [x] T026 Connect MCP server to agent via mcp_servers parameter in backend/src/agents/chat_agent.py
- [x] T027 Create function to run agent with conversation history using Runner.run() in backend/src/agents/chat_agent.py — accepts list of messages, returns agent response and tool calls
- [x] T028 Implement conversation history formatting — convert Message DB records to OpenAI message format (role/content dicts) in backend/src/agents/chat_agent.py
- [x] T029 Implement tool call extraction — parse agent response to extract tool_name, tool_input, tool_output for each tool invocation in backend/src/agents/chat_agent.py

**Checkpoint**: Agent receives messages, invokes correct MCP tools, returns natural language responses.

---

## Phase 6: Chat Service & API — US6 Conversation Persistence (Priority: P1)

**Goal**: Implement the stateless chat flow orchestrator and HTTP endpoint. Conversations persist in database.

**Independent Test**: POST to /api/{user_id}/chat with message, get response with conversation_id. POST again with same conversation_id, verify context preserved.

### Implementation

- [x] T030 Create chat service in backend/src/services/chat_service.py with function: load_or_create_conversation(user_id, conversation_id) — loads existing or creates new Conversation record
- [x] T031 Create chat service function: load_messages(conversation_id) — queries Message records ordered by created_at ascending
- [x] T032 Create chat service function: save_message(conversation_id, role, content, tool_name, tool_input, tool_output) — persists a single Message record
- [x] T033 Create chat service function: process_chat(user_id, conversation_id, message) — orchestrates the full stateless flow: load conversation, append user message, run agent, persist assistant response and tool calls, return ChatResponse
- [x] T034 Create chat API router in backend/src/api/v1/chat.py with POST /api/{user_id}/chat endpoint — validates auth, validates user_id matches JWT, calls chat service, returns ChatResponse
- [x] T035 Add input validation to chat endpoint: reject empty message (400), validate conversation_id format if provided, verify conversation ownership (404 if wrong user)
- [x] T036 Add error handling to chat endpoint: catch agent failures (500), catch DB errors (500), return consistent error format per spec
- [x] T037 Register chat router in backend/src/main.py — add chat_router to the FastAPI app with appropriate prefix
- [x] T038 Verify new conversation created when conversation_id is omitted
- [x] T039 Verify existing conversation loaded and continued when conversation_id is provided
- [x] T040 Verify all messages (user, assistant, tool) persisted in messages table after each request
- [x] T041 Verify server restart preserves conversation state — messages loaded from DB on next request

**Checkpoint**: Chat endpoint operational. Conversations persist across requests. Stateless flow verified.

---

## Phase 7: Multi-User Isolation — US7 (Priority: P1)

**Goal**: Verify complete data isolation between users.

**Independent Test**: Create tasks as user A, query as user B, verify zero results.

### Implementation

- [x] T042 Verify chat endpoint validates user_id path parameter matches JWT user_id — reject mismatched requests with 401
- [x] T043 Verify conversation_id belonging to user A returns 404 when accessed by user B
- [x] T044 Verify MCP tools filter all queries by user_id — user B cannot list, complete, update, or delete user A tasks

**Checkpoint**: Multi-user isolation confirmed at API, conversation, and MCP tool levels.

---

## Phase 8: Frontend ChatKit — US1-US7 (Priority: P1)

**Goal**: Minimal ChatKit frontend for conversational UI.

**Independent Test**: Open /chat page, type message, see response from agent.

### Implementation

- [x] T045 Add ChatKit dependency to frontend/package.json
- [x] T046 Add backend API URL to frontend/.env.local
- [x] T047 Create ChatInterface component in frontend/src/components/ChatInterface.tsx — wraps ChatKit, manages conversation_id state, sends messages to POST /api/{user_id}/chat, displays responses
- [x] T048 Create chat page in frontend/src/app/chat/page.tsx — renders ChatInterface component, passes auth token and user_id
- [x] T049 Implement auth token inclusion in chat API requests — add Authorization: Bearer header to all fetch calls in ChatInterface
- [x] T050 Verify no business logic in frontend — ChatInterface only sends messages and displays responses

**Checkpoint**: Chat page renders, messages flow to backend and back. No frontend business logic.

---

## Phase 9: Integration & Validation

**Purpose**: End-to-end testing of complete flow per spec acceptance scenarios.

- [x] T051 Test full flow: type "Add a task to buy groceries" → verify task created in DB and agent confirms
- [x] T052 Test full flow: type "Show my tasks" → verify agent lists tasks via list_tasks tool
- [x] T053 Test full flow: type "Mark buy groceries as done" → verify complete_task invoked, task completed
- [x] T054 Test full flow: type "Change priority to high" → verify update_task invoked, priority updated
- [x] T055 Test full flow: type "Delete buy groceries" → verify agent asks for confirmation before delete_task
- [x] T056 Test conversation persistence: send multiple messages in same conversation, verify context preserved
- [x] T057 Test multi-step chaining: type "Complete buy groceries and add pick up dry cleaning" → verify both tools invoked
- [x] T058 Test error handling: send empty message → verify 400 response
- [x] T059 Test error handling: reference non-existent task → verify agent offers to list tasks
- [x] T060 Test non-task query: send "What's the weather?" → verify agent redirects to task management
- [x] T061 Verify tool_calls array in API response contains all tool invocations from the request
- [x] T062 Run quickstart.md validation checklist

**Checkpoint**: All acceptance scenarios pass. System ready for hackathon review.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundation)**: Depends on Phase 1 — BLOCKS all subsequent phases
- **Phase 3 (MCP: add + list)**: Depends on Phase 2
- **Phase 4 (MCP: complete + update + delete)**: Depends on Phase 2, can run parallel to Phase 3
- **Phase 5 (Agent)**: Depends on Phases 3 + 4 (needs all MCP tools)
- **Phase 6 (Chat API)**: Depends on Phase 5 (needs agent)
- **Phase 7 (Isolation)**: Depends on Phase 6 (needs chat endpoint)
- **Phase 8 (Frontend)**: Depends on Phase 6 (needs chat endpoint)
- **Phase 9 (Integration)**: Depends on all phases

### Critical Path

```
Phase 1 → Phase 2 → Phase 3 ──┐
                     Phase 4 ──┤→ Phase 5 → Phase 6 → Phase 7 ──┐
                               │                    → Phase 8 ──┤→ Phase 9
                               └────────────────────────────────┘
```

### Parallel Opportunities

- T002 + T003 (config + package init) — different files
- T009 + T010 + T011 (schemas) — within same file but independent sections
- T018 + T019 + T020 (complete + update + delete tools) — independent tools
- Phase 3 + Phase 4 can overlap (add/list vs complete/update/delete)
- Phase 7 + Phase 8 can overlap (isolation verification + frontend)

---

## Implementation Strategy

### MVP First (Phases 1-6)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundation (T004-T011)
3. Complete Phase 3: MCP add + list (T012-T017)
4. Complete Phase 4: MCP complete + update + delete (T018-T023)
5. Complete Phase 5: Agent (T024-T029)
6. Complete Phase 6: Chat API (T030-T041)
7. **STOP and VALIDATE**: Test chat endpoint with curl
8. If working: proceed to Phase 7-9

### Incremental Delivery

- After Phase 6: Backend fully functional (test via curl/Postman)
- After Phase 8: Full UI available via ChatKit
- After Phase 9: All acceptance scenarios verified

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] labels map tasks to spec user stories for traceability
- MCP tools in Phases 3-4 can be tested independently before agent
- Agent in Phase 5 can be tested with mock conversations before API
- All 62 tasks align with spec sections 1-10, plan stages 1-6
- No code generation in this document — implementation via /sp.implement
