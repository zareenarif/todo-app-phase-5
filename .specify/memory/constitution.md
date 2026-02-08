# Todo AI Chatbot Application Constitution (Phase 3)

<!--
Sync Impact Report:
- Version change: 2.0.0 → 3.0.0
- Major version increment: Fundamental architectural transformation from
  full-stack web app to AI-powered conversational chatbot with MCP architecture
- Breaking changes:
  - Removed: Next.js frontend (replaced with OpenAI ChatKit)
  - Removed: Frontend component/page requirements (TaskList, TaskForm, etc.)
  - Removed: Responsive design requirements (ChatKit handles UI)
  - Removed: "AI/Chatbot features" from out-of-scope (now primary scope)
  - Added: OpenAI Agents SDK for AI logic
  - Added: Official MCP SDK for tool server
  - Added: MCP statelessness principles
  - Added: Conversation state persistence requirements
  - Added: Natural language → tool mapping requirements
- Modified principles:
  - Principle IV: Simplicity Over Complexity (updated for MCP/agent context)
  - Principle V: Scope Discipline (reframed for chatbot features)
  - Principle VII: Stateless Authentication → Stateless Server & MCP Tools
  - Replaced Principle VIII: User Data Isolation → MCP Tool Discipline
- Added principles:
  - Principle IX: Conversation State Persistence
  - Principle X: AI Agent Boundary Discipline
- Removed sections:
  - Frontend Requirements (pages, components, responsive design)
- Added sections:
  - MCP Architecture, AI Agent Architecture, Conversation Management
- Templates requiring updates:
  ⚠ .specify/templates/plan-template.md (pending - constitution check
    gates need MCP/agent alignment)
  ⚠ .specify/templates/spec-template.md (pending - needs MCP tool
    contract sections)
  ⚠ .specify/templates/tasks-template.md (pending - needs MCP/agent
    task types)
- Follow-up TODOs: None
- Impact: Complete transformation to AI-powered conversational todo
  chatbot with MCP-compliant stateless tool architecture
-->

## Purpose

This project follows Spec-Driven Development (SDD). The objective of
Phase 3 is to build an AI-powered conversational Todo chatbot using
Model Context Protocol (MCP) architecture, where users interact with
their tasks through natural language via an AI agent.

All development decisions MUST be guided by this constitution and the
approved specification. No implementation may begin until the
specification, plan, and tasks are agreed upon.

**Phase Transition:** Phase 3 builds upon the Phase 2 foundation by
replacing the traditional web UI with a conversational AI interface
powered by OpenAI Agents SDK, exposing all task operations through
stateless MCP tools.

**Hackathon Context:** This is a hackathon evaluation environment.
Architectural correctness, stateless compliance, tool usage accuracy,
and MCP compliance are the primary evaluation criteria. UI polish is
secondary to architectural soundness.

## Core Principles

### I. Specification Before Implementation

All features MUST be specified before any code is written. The
specification defines what will be built, why it is needed, and what
success looks like.

**Non-negotiable rules:**
- No coding without an approved specification
- Specifications MUST be concrete and testable
- Requirements MUST be clear and unambiguous
- MCP tool contracts MUST be explicitly defined
- AI agent behavior MUST include acceptance criteria

**Rationale:** Specifications prevent scope creep, ensure alignment,
and provide a shared understanding. For MCP-based systems,
specifications serve as contracts between the AI agent, MCP tools,
and the database layer.

### II. Planning Before Coding

All implementations MUST have an architectural plan approved before
code is generated. The plan defines how the specification will be
achieved technically across the MCP stack.

**Non-negotiable rules:**
- No coding without an approved implementation plan
- Plans MUST identify all components (ChatKit frontend, FastAPI
  backend, MCP server, AI agent) and their interactions
- Plans MUST define MCP tool schemas, request/response contracts,
  and database models
- Plans MUST address authentication flow and statelessness
- Plans MUST specify conversation state management strategy

**Rationale:** Planning ensures technical decisions are deliberate
and documented. It prevents reactive coding and validates that MCP
tools, AI agent logic, and database designs align.

### III. Tasks Before Execution

All work MUST be broken down into discrete, testable tasks before
execution begins.

**Non-negotiable rules:**
- No execution without a defined task list
- Each task MUST be independently verifiable
- Tasks MUST reference specific files, endpoints, and MCP tools
- Tasks MUST specify layer: MCP server, AI agent, backend API,
  frontend, or database
- Tasks MUST identify dependencies

**Rationale:** Task decomposition ensures work is trackable, testable,
and completable in small increments across MCP architecture layers.

### IV. Simplicity Over Complexity

The implementation MUST be as simple as possible while meeting all
requirements. Complexity requires explicit justification.

**Non-negotiable rules:**
- Use established frameworks and patterns (FastAPI, MCP SDK, OpenAI
  Agents SDK)
- No custom protocol implementations (use Official MCP SDK)
- No unnecessary abstraction layers
- Clear, readable code over clever solutions
- Leverage SDK defaults unless requirements demand customization
- MCP tools MUST be thin wrappers around task operations

**Rationale:** Simplicity reduces bugs and improves evaluation scores.
In hackathon context, simplicity means using SDK conventions and
standard MCP patterns rather than inventing custom solutions.

### V. Scope Discipline

This project maintains strict scope discipline. Only features
explicitly defined in the Phase 3 specification may be implemented.

**Non-negotiable rules:**
- ALL features MUST follow SDD workflow: specification → plan →
  tasks → implementation
- No features may be added without user-approved specification
- Follow hackathon requirements EXACTLY — no feature creep
- No UI or backend work unless explicitly defined in the spec
- Explicitly out of scope:
  - Kubernetes orchestration
  - Cloud-specific infrastructure code
  - Background worker processes
  - Admin panels or user management dashboards
  - Custom UI components beyond ChatKit integration
  - Direct database access by the AI agent
  - Business logic inside the frontend

**Rationale:** Scope discipline is critical for hackathon success.
Every unspecified feature is wasted effort and potential point
deduction for architectural violations.

### VI. Security by Design

Security MUST be built into every layer of the application.

**Non-negotiable rules:**
- All API endpoints MUST require valid authentication (except auth
  endpoints)
- All user input MUST be validated and sanitized
- All database queries MUST use parameterized statements (SQLModel
  ORM enforced)
- Secrets MUST be stored in environment variables, never in code
- CORS policies MUST be explicitly configured
- SQL injection, XSS, and CSRF MUST be prevented by design

**Rationale:** Security vulnerabilities compromise user data and
reduce hackathon evaluation scores.

### VII. Stateless Server & MCP Tools

The backend server and all MCP tools MUST be stateless. No
server-side session storage or in-memory state is permitted.

**Non-negotiable rules:**
- The FastAPI server MUST be stateless
- MCP tools MUST be stateless — no in-memory caching of user data
- MCP tools MUST ONLY expose task operations (CRUD)
- Each MCP tool invocation MUST be self-contained
- All state MUST be persisted in the database
- Authentication MUST use Better Auth with stateless token
  verification
- Requests without valid authentication MUST be rejected

**Rationale:** Statelessness is a critical evaluation criterion.
MCP tools that maintain state violate the protocol's design
principles and will fail compliance checks.

### VIII. MCP Tool Discipline

MCP tools MUST be the exclusive interface between the AI agent and
task data. No shortcuts or bypasses are permitted.

**Non-negotiable rules:**
- AI agent MUST use MCP tools for ALL task actions
- No direct database access by the AI agent
- MCP tools MUST ONLY expose task operations (create, read, update,
  delete, list, complete)
- Each MCP tool MUST have a clear, single responsibility
- Tool input/output schemas MUST be explicitly defined
- Natural language → tool mapping MUST be exact and deterministic
- Tool responses MUST be structured for AI agent consumption

**Rationale:** MCP compliance is mandatory for hackathon evaluation.
The agent-tool boundary enforces separation of concerns and ensures
the system is auditable and testable.

### IX. Conversation State Persistence

Conversation state MUST be persisted in the database. No in-memory
conversation tracking is permitted.

**Non-negotiable rules:**
- All conversation history MUST be stored in the database
- Conversation context MUST survive server restarts
- Each conversation MUST be associated with an authenticated user
- The AI agent MUST be able to resume conversations from persisted
  state
- No in-memory conversation buffers or caches

**Rationale:** Conversation persistence is required for stateless
server compliance. Users expect conversation continuity, and the
evaluation criteria require database-backed state management.

### X. AI Agent Boundary Discipline

The AI agent MUST operate within strict boundaries. It receives
natural language input, maps it to MCP tool calls, and returns
natural language responses.

**Non-negotiable rules:**
- The AI agent MUST use OpenAI Agents SDK
- The agent MUST NOT contain business logic — only tool orchestration
- The agent MUST map natural language to appropriate MCP tool calls
- The agent MUST NOT access the database directly
- The agent MUST NOT modify data except through MCP tools
- The agent MUST handle ambiguous input by asking clarifying
  questions
- The agent MUST provide helpful, conversational responses

**Rationale:** Clean agent boundaries ensure architectural
correctness and testability. The agent is a translator between
natural language and MCP tools, not a business logic container.

## Technology Stack

The following technologies are REQUIRED and MUST be used exactly
as specified:

### Frontend
- **UI Framework:** OpenAI ChatKit (conversational interface)
- **Purpose:** Chat-based interaction with the AI todo agent
- **Constraint:** No business logic inside the frontend

### Backend
- **Framework:** Python FastAPI (async where beneficial)
- **Language:** Python 3.11+
- **ORM:** SQLModel (Pydantic-based, type-safe)
- **Validation:** Pydantic models for request/response validation

### AI Logic
- **Framework:** OpenAI Agents SDK
- **Purpose:** Natural language understanding and MCP tool
  orchestration
- **Constraint:** Agent MUST use MCP tools for all task actions

### MCP Server
- **Framework:** Official MCP SDK
- **Purpose:** Expose task operations as stateless MCP tools
- **Constraint:** Tools MUST be stateless, MUST only expose task
  operations

### Database
- **Database:** Neon Serverless PostgreSQL
- **ORM:** SQLModel
- **Connection:** PostgreSQL connection string from environment
  variable

### Authentication
- **Auth Provider:** Better Auth
- **Constraint:** Stateless token-based authentication

### Development & Tooling
- **Spec-Driven Development:** Claude Code + Spec-Kit Plus
- **Code Generation:** Claude Code (ALL code MUST be generated,
  NO manual coding by humans)
- **Version Control:** Git with semantic commit messages
- **Environment Variables:** `.env` files (never committed)

**Rationale:** This stack satisfies all hackathon requirements:
OpenAI ChatKit for conversational UI, Agents SDK for AI logic,
MCP SDK for tool protocol compliance, FastAPI for backend,
SQLModel + Neon PostgreSQL for persistence, Better Auth for
authentication.

## Technical Constraints

### Architecture
- **MCP Compliance:** All task operations MUST go through MCP tools
- **Stateless Backend:** Server MUST NOT maintain session state
- **Stateless MCP Tools:** Tools MUST NOT cache or store state
- **Agent Boundary:** AI agent MUST NOT access database directly
- **Frontend Boundary:** No business logic in ChatKit frontend
- **Conversation Persistence:** All state in the database

### MCP Tool Requirements
- Tools MUST be stateless
- Tools MUST only expose task operations
- Tool schemas MUST be explicitly defined
- Tool responses MUST be structured JSON
- Each tool MUST have a single, clear responsibility

### Database Constraints
- **ORM Required:** All database access MUST use SQLModel
- **User Isolation:** Every user-data table MUST have `user_id`
- **Timestamps:** All tables MUST have `created_at` and `updated_at`
- **Conversation Storage:** Conversation history MUST be persisted

### Deployment Constraints
- **Containerization:** Not required
- **Orchestration:** No Kubernetes or cloud orchestration
- **Background Workers:** Not permitted
- **Admin Dashboards:** Not permitted

## MCP Architecture

### Tool Design Principles
1. Each tool has ONE responsibility (e.g., create_task, list_tasks)
2. Tools receive all needed context via parameters (stateless)
3. Tools return structured responses for agent consumption
4. Tools validate input and return clear error messages
5. Tools enforce user isolation (filter by authenticated user_id)

### Required MCP Tools
- `create_task` — Create a new task
- `list_tasks` — List tasks with optional filters
- `get_task` — Get a single task by ID
- `update_task` — Update task fields
- `delete_task` — Delete a task
- `complete_task` — Toggle task completion status

### Tool Flow
1. User sends natural language message via ChatKit
2. AI agent (OpenAI Agents SDK) interprets the message
3. Agent maps intent to one or more MCP tool calls
4. MCP tools execute against the database via SQLModel
5. Tool responses returned to agent
6. Agent formulates natural language response
7. Response displayed in ChatKit

## AI Agent Architecture

### Agent Responsibilities
- Parse natural language intent from user messages
- Map intent to appropriate MCP tool calls
- Handle multi-step operations (e.g., "mark all overdue tasks done")
- Ask clarifying questions when intent is ambiguous
- Provide helpful, conversational responses
- Maintain conversation context via persisted state

### Agent Constraints
- MUST use OpenAI Agents SDK
- MUST NOT contain business logic
- MUST NOT access database directly
- MUST use MCP tools for ALL data operations
- MUST handle errors gracefully with user-friendly messages

## Data Model Rules

### Task Entity (REQUIRED fields)

**Core Fields:**
- `id` — UUID primary key (auto-generated)
- `user_id` — UUID foreign key to users table (REQUIRED, indexed)
- `title` — String, required, non-empty (max 200 chars)
- `description` — String, optional (max 2000 chars)
- `completed` — Boolean, default False
- `created_at` — Timestamp, auto-generated
- `updated_at` — Timestamp, auto-updated

**Extended Fields:**
- `priority` — Enum: 'high' | 'medium' | 'low' | null
- `tags` — Array of strings
- `due_date` — Date, optional
- `recurrence` — Enum: 'daily' | 'weekly' | 'monthly' | null

### Conversation Entity (REQUIRED fields)
- `id` — UUID primary key
- `user_id` — UUID foreign key (REQUIRED, indexed)
- `messages` — JSON array of message objects
- `created_at` — Timestamp
- `updated_at` — Timestamp

### User Entity (REQUIRED fields)
Managed by Better Auth, but backend MUST reference:
- `id` — UUID primary key
- `email` — String, unique, indexed
- `name` — String, optional
- `created_at` — Timestamp

## Environment Variables (REQUIRED)
- `DATABASE_URL` — Neon PostgreSQL connection string
- `BETTER_AUTH_SECRET` — Shared secret for authentication
- `OPENAI_API_KEY` — OpenAI API key for Agents SDK
- `CORS_ORIGINS` — Allowed frontend origins

## Evaluation Criteria Awareness

The following evaluation priorities MUST guide all decisions:

1. **Architectural correctness > UI polish** — Get the MCP
   architecture right before worrying about ChatKit appearance
2. **Stateless correctness is critical** — Server and MCP tools
   MUST be verifiably stateless
3. **Tool usage accuracy is critical** — MCP tools MUST work
   correctly and be properly invoked
4. **Natural language → tool mapping MUST be exact** — Agent MUST
   reliably map user intent to correct tool calls
5. **MCP compliance is mandatory** — Protocol adherence is
   non-negotiable

## Quality Standards

**Backend:**
- Type hints on all functions
- Pydantic models for all request/response schemas
- Async/await for I/O operations where beneficial
- Proper error handling with appropriate status codes
- All endpoints include API documentation (OpenAPI/Swagger)

**MCP Tools:**
- Each tool MUST have clear input/output schemas
- Each tool MUST validate inputs
- Each tool MUST handle errors gracefully
- Each tool MUST enforce user isolation

**AI Agent:**
- Agent MUST handle edge cases (empty input, ambiguous requests)
- Agent MUST provide helpful error messages
- Agent MUST not hallucinate tool capabilities

**General:**
- Clean and readable code (self-documenting)
- Small, focused functions with single responsibilities
- No dead code or unused imports
- No hardcoded secrets or environment-specific values

## Testing Requirements

**Manual Testing (REQUIRED before deployment):**
- All MCP tools tested independently
- AI agent tested with natural language inputs
- Conversation persistence verified
- Multi-user isolation tested
- Statelessness verified (server restart preserves state)
- Error cases tested (invalid input, unauthorized access)
- Natural language → tool mapping accuracy tested

## Governance

This constitution supersedes all other development practices. Any
amendments MUST be documented with rationale and approved before
taking effect.

**Compliance:**
- All specifications, plans, and tasks MUST be verified against
  this constitution
- Any complexity introduced MUST be justified explicitly
- ALL code generation MUST be performed by Claude Code (no manual
  coding by humans)
- MCP compliance MUST be verified at every stage

**Amendment Process:**
- Amendments require explicit documentation of change and rationale
- Version MUST be incremented per semantic versioning:
  - MAJOR: Breaking changes to architecture, stack, or principles
  - MINOR: New principles, requirements, or substantial additions
  - PATCH: Clarifications, typo fixes, non-breaking refinements
- All dependent templates and docs MUST be updated
- All active features MUST be reviewed for compliance after amendments

**Version:** 3.0.0 | **Ratified:** 2026-01-05 | **Last Amended:** 2026-02-08

## Amendment History

### Version 3.0.0 (2026-02-08)

**Amendment:** Complete architectural transformation to AI-powered
conversational chatbot with MCP architecture

**Rationale:** Phase 3 evolves the full-stack web application into
an AI-powered conversational todo chatbot. Users interact via natural
language through OpenAI ChatKit, with an AI agent (OpenAI Agents SDK)
orchestrating task operations through stateless MCP tools.

**Major Changes:**
- **Frontend:** Next.js replaced with OpenAI ChatKit
- **AI Logic:** Added OpenAI Agents SDK for agent orchestration
- **MCP Server:** Added Official MCP SDK for stateless tool exposure
- **Architecture:** Traditional CRUD web app → conversational AI
  chatbot with MCP tool layer
- **Principles:** Added MCP Tool Discipline (VIII), Conversation
  State Persistence (IX), AI Agent Boundary Discipline (X)
- **Scope:** AI/Chatbot features moved from out-of-scope to primary
  scope
- **Data Model:** Added Conversation entity for state persistence
- **Evaluation:** Added hackathon evaluation criteria awareness

**Breaking Changes from Phase 2:**
- Next.js frontend replaced with OpenAI ChatKit
- Traditional UI components removed (TaskList, TaskForm, etc.)
- Direct API calls replaced with MCP tool invocations via AI agent
- Added AI agent layer between user and backend
- Added MCP server layer between agent and database

**Preserved from Phase 2:**
- FastAPI backend framework
- SQLModel ORM + Neon PostgreSQL
- Better Auth authentication
- Task data model (all fields preserved)
- User data isolation principles
- Core SDD principles
- Security by design

### Version 2.0.0 (2026-01-05)

**Amendment:** Complete architectural transformation to full-stack
web application

**Rationale:** Phase 2 evolved the CLI application into a
production-ready web application with secure authentication,
persistent storage, and multi-user support.

**Major Changes:**
- Added Next.js 16+ (frontend), FastAPI (backend), Neon PostgreSQL
  (database), Better Auth (authentication)
- Transformed from single-layer CLI to three-layer full-stack
- Replaced in-memory storage with persistent PostgreSQL
- Added stateless JWT-based authentication
- Added user isolation and data separation
- Added security-focused principles (VI, VII, VIII)

### Version 1.2.0 (2026-01-04)

**Amendment:** Extended Task Entity Rules for advanced task management

### Version 1.1.0 (2026-01-03)

**Amendment:** Updated Principle V from "No Features Beyond Phase I
Scope" to "Scope Discipline and Controlled Enhancement"
