# Tasks: Cloud-Native Event-Driven Todo AI Chatbot

**Input**: Design documents from `/specs/010-cloud-native-deployment/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, quickstart.md

**Tests**: Not explicitly requested in spec. Test tasks omitted per template rules.

**Organization**: Tasks grouped by user story (8 stories, P1–P8) to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Exact file paths included in all descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`, `helm/todo-chatbot/`, `.github/workflows/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Install Dapr dependencies, create event envelope schemas, extend configuration, and prepare database migrations for new entities.

- [ ] T001 Add `dapr` and `dapr-ext-fastapi` to `backend/requirements.txt`
  - **Purpose**: Enable Dapr Python SDK for pub/sub publishing and subscription decorators
  - **Input**: research.md R2 (Dapr Python SDK decision)
  - **Tool**: Claude Code
  - **Expected output**: `backend/requirements.txt` updated with `dapr>=1.13`, `dapr-ext-fastapi>=1.13`, `python-dateutil>=2.8`

- [ ] T002 Extend backend configuration with Dapr environment variables in `backend/src/core/config.py`
  - **Purpose**: Add Dapr-related config vars (pubsub component name, app port, sidecar port)
  - **Input**: plan.md Architecture: Dapr Building Blocks
  - **Tool**: Claude Code
  - **Expected output**: `config.py` extended with `DAPR_PUBSUB_NAME`, `DAPR_HTTP_PORT`, `DAPR_GRPC_PORT` settings with sensible defaults

- [ ] T003 [P] Create event envelope schema in `backend/src/events/schemas.py`
  - **Purpose**: Define CloudEvents-compatible event envelope (id, source, type, time, data) used by all event publishers
  - **Input**: data-model.md TaskEvent / ReminderEvent definitions, research.md R4
  - **Tool**: Claude Code
  - **Expected output**: Pydantic models `TaskEvent` and `ReminderEvent` with UUID id, source string, type enum, ISO timestamp, and data dict

- [ ] T004 [P] Create Reminder SQLModel entity in `backend/src/models/reminder.py`
  - **Purpose**: Define the Reminder database model for scheduled task reminders
  - **Input**: data-model.md Reminder table definition
  - **Tool**: Claude Code
  - **Expected output**: `Reminder` SQLModel with fields: id, user_id, task_id, remind_at, lead_time, status (PENDING/TRIGGERED/CANCELLED), created_at, updated_at

- [ ] T005 [P] Create AuditLogEntry SQLModel entity in `backend/src/models/audit_log.py`
  - **Purpose**: Define the append-only audit log database model
  - **Input**: data-model.md AuditLogEntry table definition
  - **Tool**: Claude Code
  - **Expected output**: `AuditLogEntry` SQLModel with fields: id, event_id (unique), event_type, user_id, task_id, timestamp, payload (JSON), created_at

- [ ] T006 Create Alembic migration for reminder and audit_log tables in `backend/alembic/versions/`
  - **Purpose**: Generate database migration to create new tables with all constraints and indexes
  - **Input**: data-model.md Migration Plan (T004, T005 models)
  - **Tool**: Claude Code
  - **Expected output**: Migration file `add_reminder_and_audit_tables.py` creating both tables with FK constraints, unique index on event_id, composite index on (user_id, timestamp)

---

## Phase 2: Foundational — Event Publishing Infrastructure (Blocking Prerequisites)

**Purpose**: Core event publishing service and Dapr integration that ALL user stories depend on. No user story work can begin until this phase is complete.

**⚠️ CRITICAL**: US1–US8 all depend on this phase.

- [ ] T007 Create event publisher service in `backend/src/services/event_publisher.py`
  - **Purpose**: Central service for publishing domain events to Kafka via Dapr Pub/Sub sidecar
  - **Input**: plan.md Event Publishing Flow, research.md R2 (DaprClient.publish_event)
  - **Tool**: Claude Code
  - **Expected output**: `EventPublisherService` class with methods `publish_task_event(event_type, task, user_id)` and `publish_reminder_event(reminder)`, using `DaprClient` to POST to Dapr sidecar

- [ ] T008 Create event schemas (request/response) in `backend/src/schemas/events.py`
  - **Purpose**: Define Pydantic schemas for event payloads serialized to Kafka topics
  - **Input**: data-model.md TaskEvent, plan.md event envelope format
  - **Tool**: Claude Code
  - **Expected output**: `TaskEventPayload`, `ReminderEventPayload` Pydantic models with validation

- [ ] T009 Create Dapr subscription event handlers in `backend/src/events/handlers.py`
  - **Purpose**: Define FastAPI routes that receive events from Dapr subscriptions (POST /events/<topic>)
  - **Input**: plan.md Subscription Routes table
  - **Tool**: Claude Code
  - **Expected output**: FastAPI router with handlers for `/events/task-events`, `/events/task-updates`, `/events/reminders` that dispatch to appropriate service

- [ ] T010 Register Dapr subscription routes in backend FastAPI app (`backend/src/main.py` or equivalent)
  - **Purpose**: Wire event handler router into the FastAPI application
  - **Input**: T009 handlers, plan.md subscription routes
  - **Tool**: Claude Code
  - **Expected output**: `main.py` includes the events router; Dapr `@app.subscribe` decorators or programmatic subscription registered

**Checkpoint**: Event publishing infrastructure ready — user story implementation can begin.

---

## Phase 3: User Story 1 — Event-Driven Task Operations (Priority: P1) 🎯 MVP

**Goal**: All task CRUD operations publish domain events to Kafka via Dapr. Downstream consumers (audit, recurrence, reminders) can react asynchronously.

**Independent Test**: Create, update, complete, and delete a task via chatbot → verify events appear on `todo.task-events` and `todo.task-updates` Kafka topics.

### Implementation for User Story 1

- [ ] T011 [US1] Integrate event publishing into task create operation in `backend/src/api/v1/tasks.py`
  - **Purpose**: After successful DB write on task creation, publish `task.created` event
  - **Input**: T007 EventPublisherService, spec.md US1 scenario 1
  - **Tool**: Claude Code
  - **Expected output**: `create_task` endpoint calls `event_publisher.publish_task_event("task.created", task, user_id)` after DB commit

- [ ] T012 [US1] Integrate event publishing into task update operation in `backend/src/api/v1/tasks.py`
  - **Purpose**: After successful DB write on task update, publish `task.updated` event with before/after state
  - **Input**: T007 EventPublisherService, spec.md US1 scenario 2
  - **Tool**: Claude Code
  - **Expected output**: `update_task` endpoint captures before-state, commits update, publishes `task.updated` event with diff

- [ ] T013 [US1] Integrate event publishing into task complete operation in `backend/src/api/v1/tasks.py`
  - **Purpose**: After marking task completed, publish `task.completed` event
  - **Input**: T007 EventPublisherService, spec.md US1 scenario 3
  - **Tool**: Claude Code
  - **Expected output**: `complete_task` endpoint publishes `task.completed` event after DB commit

- [ ] T014 [US1] Integrate event publishing into task delete operation in `backend/src/api/v1/tasks.py`
  - **Purpose**: After task deletion, publish `task.deleted` event with task_id and user_id
  - **Input**: T007 EventPublisherService, spec.md US1 scenario 4
  - **Tool**: Claude Code
  - **Expected output**: `delete_task` endpoint publishes `task.deleted` event after DB commit

- [ ] T015 [US1] Integrate event publishing into MCP tools in `backend/src/mcp/tools.py`
  - **Purpose**: Extend existing MCP tools (add_task, update_task, complete_task, delete_task) to publish events after DB operations
  - **Input**: spec.md FR-033 (MCP tools MUST publish events), T007
  - **Tool**: Claude Code
  - **Expected output**: Each MCP tool calls `event_publisher.publish_task_event()` after successful DB write

- [ ] T016 [US1] Add Dapr resiliency policy handling for failed event publishes in `backend/src/services/event_publisher.py`
  - **Purpose**: Ensure task operations succeed even when Kafka is unavailable; events retried via Dapr resiliency
  - **Input**: spec.md US1 scenario 5, plan.md Dapr Resiliency
  - **Tool**: Claude Code
  - **Expected output**: `event_publisher` wraps publish calls in try/except, logs failures, relies on Dapr retry policy; DB write is never blocked

**Checkpoint**: US1 complete — all task mutations publish events. Testable independently.

---

## Phase 4: User Story 2 — Task Search, Filter, and Sort (Priority: P2)

**Goal**: Users can search tasks by keyword, filter by priority/status/tags/due date, and sort by various criteria via both REST API and MCP tools.

**Independent Test**: Create tasks with varied attributes → search/filter/sort via chatbot → verify correct results returned.

### Implementation for User Story 2

- [ ] T017 [P] [US2] Create search/filter/sort query parameter schemas in `backend/src/schemas/task.py`
  - **Purpose**: Define Pydantic models for search, filter, and sort query parameters
  - **Input**: plan.md Extended Query Parameters table, spec.md FR-002 to FR-005
  - **Tool**: Claude Code
  - **Expected output**: `TaskSearchParams` schema with: search (str), status (enum), priority (enum), tags (str), due_date_from (date), due_date_to (date), sort (enum), order (enum)

- [ ] T018 [US2] Extend task list endpoint with search/filter/sort in `backend/src/api/v1/tasks.py`
  - **Purpose**: Add query parameter parsing and SQLAlchemy query building for filtered/sorted task retrieval
  - **Input**: T017 schemas, spec.md US2 scenarios 1–6
  - **Tool**: Claude Code
  - **Expected output**: `list_tasks` endpoint accepts `TaskSearchParams`, builds dynamic query with ILIKE search, enum filters, date range filters, and ORDER BY clause

- [ ] T019 [US2] Extend MCP `list_tasks` tool with search/filter/sort parameters in `backend/src/mcp/tools.py`
  - **Purpose**: Allow chatbot users to search, filter, and sort tasks via natural language → MCP tool
  - **Input**: spec.md FR-031, T018 query logic
  - **Tool**: Claude Code
  - **Expected output**: MCP `list_tasks` tool accepts search/filter/sort params and delegates to the same query logic as the REST endpoint

**Checkpoint**: US2 complete — search, filter, and sort work via both API and chatbot.

---

## Phase 5: User Story 3 — Reminders (Priority: P3)

**Goal**: Users can set, cancel, and list reminders on tasks. Reminders fire at scheduled times via Dapr Jobs API and publish events.

**Independent Test**: Create a task with due date → set reminder → verify reminder fires and event is published to `todo.reminders`.

### Implementation for User Story 3

- [ ] T020 [P] [US3] Create reminder request/response schemas in `backend/src/schemas/reminder.py`
  - **Purpose**: Define Pydantic models for reminder CRUD operations
  - **Input**: data-model.md Reminder entity, plan.md Reminder Lead Times
  - **Tool**: Claude Code
  - **Expected output**: `ReminderCreate` (task_id, lead_time enum), `ReminderResponse` (full reminder fields), `ReminderListResponse`

- [ ] T021 [US3] Implement reminder service in `backend/src/services/reminder_service.py`
  - **Purpose**: Business logic for creating, cancelling, listing reminders and registering Dapr Jobs
  - **Input**: plan.md Reminder System Flow, research.md R3 (Dapr Jobs API)
  - **Tool**: Claude Code
  - **Expected output**: `ReminderService` with methods: `create_reminder(task_id, lead_time, user_id)` (calculates remind_at, saves to DB, registers Dapr Job), `cancel_reminder(reminder_id, user_id)`, `list_reminders(user_id)`, `suppress_if_completed(task_id)`

- [ ] T022 [US3] Create reminder CRUD endpoints in `backend/src/api/v1/reminders.py`
  - **Purpose**: REST API endpoints for reminder management
  - **Input**: T020 schemas, T021 service, spec.md FR-006 to FR-010
  - **Tool**: Claude Code
  - **Expected output**: FastAPI router with `POST /api/v1/reminders` (set), `DELETE /api/v1/reminders/{id}` (cancel), `GET /api/v1/reminders` (list), `PUT /api/v1/reminders/{id}` (update)

- [ ] T023 [US3] Register reminder router in backend app (`backend/src/main.py`)
  - **Purpose**: Wire the reminder API router into the FastAPI application
  - **Input**: T022 router
  - **Tool**: Claude Code
  - **Expected output**: `main.py` includes `reminders.router` with prefix `/api/v1/reminders`

- [ ] T024 [US3] Implement reminder event handler in `backend/src/events/handlers.py`
  - **Purpose**: Handle `reminder.triggered` events from Dapr Jobs; update reminder status, suppress if task completed
  - **Input**: plan.md Reminder Flow steps 4–6, spec.md US3 scenarios 4–5
  - **Tool**: Claude Code
  - **Expected output**: Handler for `/events/reminders` that updates reminder status to TRIGGERED or CANCELLED based on task state

- [ ] T025 [US3] Add MCP tools for reminder management in `backend/src/mcp/tools.py`
  - **Purpose**: Allow chatbot users to set, cancel, and list reminders via natural language
  - **Input**: spec.md FR-032 (set_reminder, cancel_reminder, list_reminders)
  - **Tool**: Claude Code
  - **Expected output**: Three new MCP tools: `set_reminder`, `cancel_reminder`, `list_reminders` delegating to `ReminderService`

- [ ] T026 [US3] Add reminder suppression on task complete/delete in `backend/src/events/handlers.py`
  - **Purpose**: When a task is completed or deleted, cancel any pending reminders for that task
  - **Input**: spec.md US3 scenarios 4–5, plan.md Reminder Flow
  - **Tool**: Claude Code
  - **Expected output**: `task.completed` and `task.deleted` event handlers call `reminder_service.suppress_if_completed(task_id)`

**Checkpoint**: US3 complete — reminders can be set, fire, and are suppressed correctly.

---

## Phase 6: User Story 4 — Recurring Tasks (Priority: P4)

**Goal**: When a recurring task is completed, the system automatically generates the next instance with the correct due date.

**Independent Test**: Create a recurring (DAILY) task → complete it → verify a new task instance is auto-created with due_date + 1 day.

### Implementation for User Story 4

- [ ] T027 [US4] Implement recurrence service in `backend/src/services/recurrence_service.py`
  - **Purpose**: Listen for `task.completed` events; if task has recurrence, generate next instance with calculated due date
  - **Input**: plan.md Recurring Task Generation Flow, plan.md Due Date Calculation table
  - **Tool**: Claude Code
  - **Expected output**: `RecurrenceService` with method `handle_task_completed(event)` that checks recurrence field, calculates next due_date (DAILY +1d, WEEKLY +7d, MONTHLY +1 calendar month via dateutil), creates new task, publishes `task.created` event

- [ ] T028 [US4] Wire recurrence handler into task-events subscription in `backend/src/events/handlers.py`
  - **Purpose**: Route `task.completed` events (with recurrence set) to the recurrence service
  - **Input**: plan.md Subscription Routes table (recurrence_service), T027
  - **Tool**: Claude Code
  - **Expected output**: `/events/task-events` handler checks event type; if `task.completed` and `data.recurrence` is set, calls `recurrence_service.handle_task_completed(event)`

- [ ] T029 [US4] Add validation: recurring tasks MUST have due_date in `backend/src/api/v1/tasks.py`
  - **Purpose**: Reject creation of recurring tasks without a due_date (edge case from spec)
  - **Input**: spec.md Edge Cases ("Recurring tasks MUST have a due date")
  - **Tool**: Claude Code
  - **Expected output**: `create_task` and `update_task` endpoints validate that if `recurrence` is set, `due_date` must also be set; return 422 otherwise

**Checkpoint**: US4 complete — recurring tasks auto-generate next instances on completion.

---

## Phase 7: User Story 5 — Audit Log via Event Consumers (Priority: P5)

**Goal**: Append-only audit log captures all task operations via Kafka consumers with idempotent processing.

**Independent Test**: Perform CRUD operations on tasks → query audit log endpoint → verify all events recorded with correct metadata.

### Implementation for User Story 5

- [ ] T030 [P] [US5] Create audit log response schema in `backend/src/schemas/audit.py`
  - **Purpose**: Define Pydantic response models for audit log queries
  - **Input**: data-model.md AuditLogEntry, spec.md FR-015 to FR-017
  - **Tool**: Claude Code
  - **Expected output**: `AuditLogResponse` schema with all audit_log fields, `AuditLogListResponse` with pagination

- [ ] T031 [US5] Implement audit service (event consumer) in `backend/src/services/audit_service.py`
  - **Purpose**: Consume task events and persist audit log entries with idempotent deduplication
  - **Input**: plan.md Subscription Routes (audit_service), research.md R8 (event ID deduplication)
  - **Tool**: Claude Code
  - **Expected output**: `AuditService` with method `log_event(event)` that checks `event_id` uniqueness (via DB unique constraint), persists `AuditLogEntry`, and handles duplicates gracefully

- [ ] T032 [US5] Wire audit service into event handlers in `backend/src/events/handlers.py`
  - **Purpose**: Route all task events (created, updated, completed, deleted) to audit service
  - **Input**: plan.md Subscription Routes table, T031
  - **Tool**: Claude Code
  - **Expected output**: `/events/task-events` and `/events/task-updates` handlers call `audit_service.log_event(event)` for every event

- [ ] T033 [US5] Create audit log query endpoints in `backend/src/api/v1/audit.py`
  - **Purpose**: REST API for querying audit log by user_id, event_type, date range
  - **Input**: T030 schemas, spec.md US5 scenario 2
  - **Tool**: Claude Code
  - **Expected output**: FastAPI router with `GET /api/v1/audit` (filtered by user_id, with pagination), registered in `main.py`

- [ ] T034 [US5] Register audit router in backend app (`backend/src/main.py`)
  - **Purpose**: Wire the audit API router into the FastAPI application
  - **Input**: T033 router
  - **Tool**: Claude Code
  - **Expected output**: `main.py` includes `audit.router` with prefix `/api/v1/audit`

**Checkpoint**: US5 complete — audit log captures all task mutations, queryable via API.

---

## Phase 8: User Story 6 — Local Kubernetes Deployment with Dapr and Kafka (Priority: P6)

**Goal**: Deploy the full system (app + Kafka + Dapr) on Minikube via Helm. All pods Running, events flowing end-to-end.

**Independent Test**: `helm install` on Minikube → all pods Running within 5 minutes → create task → verify event on Kafka topic.

### Implementation for User Story 6

- [ ] T035 [P] [US6] Update Helm chart metadata in `helm/todo-chatbot/Chart.yaml`
  - **Purpose**: Bump chart version to 2.0.0, add Strimzi Kafka as dependency
  - **Input**: plan.md Chart.yaml updates, research.md R1 (Strimzi)
  - **Tool**: Helm / Claude Code
  - **Expected output**: `Chart.yaml` with version 2.0.0, Kafka dependency declared

- [ ] T036 [P] [US6] Create Dapr Pub/Sub component manifest in `helm/todo-chatbot/templates/dapr-pubsub.yaml`
  - **Purpose**: Define Dapr Pub/Sub component pointing to Kafka broker
  - **Input**: plan.md Dapr Building Blocks table (pubsub-kafka)
  - **Tool**: Helm / Claude Code
  - **Expected output**: Kubernetes manifest for Dapr Component (kind: Component, type: pubsub.kafka) with broker address templated from values

- [ ] T037 [P] [US6] Create Dapr subscription manifest in `helm/todo-chatbot/templates/dapr-subscription.yaml`
  - **Purpose**: Declare Dapr topic subscriptions routing events to backend handler endpoints
  - **Input**: plan.md Subscription Routes table, Dead Letter Handling table
  - **Tool**: Helm / Claude Code
  - **Expected output**: Dapr Subscription CRD mapping topics (todo.task-events, todo.task-updates, todo.reminders) to handler routes with dead letter topics configured

- [ ] T038 [P] [US6] Create Dapr resiliency policy in `helm/todo-chatbot/templates/dapr-resiliency.yaml`
  - **Purpose**: Define retry and circuit breaker policies for pub/sub operations
  - **Input**: plan.md Dapr Resiliency, spec.md FR-019 (dead letter topics), US1 scenario 5
  - **Tool**: Helm / Claude Code
  - **Expected output**: Dapr Resiliency CRD with 3 retries, exponential backoff, circuit breaker for pubsub-kafka component

- [ ] T039 [P] [US6] Create Dapr secrets component in `helm/todo-chatbot/templates/dapr-secrets.yaml`
  - **Purpose**: Configure Dapr to read secrets from Kubernetes Secrets
  - **Input**: plan.md Dapr Building Blocks (secrets-kubernetes)
  - **Tool**: Helm / Claude Code
  - **Expected output**: Dapr Component (kind: Component, type: secretstores.kubernetes) with namespace-scoped access

- [ ] T040 [US6] Update backend deployment with Dapr sidecar annotations in `helm/todo-chatbot/templates/backend-deployment.yaml`
  - **Purpose**: Enable Dapr sidecar injection on backend pods
  - **Input**: plan.md backend-deployment.yaml updates
  - **Tool**: Helm / Claude Code
  - **Expected output**: Backend Deployment with annotations: `dapr.io/enabled: "true"`, `dapr.io/app-id: "todo-backend"`, `dapr.io/app-port: "8000"`, `dapr.io/enable-api-logging: "true"`

- [ ] T041 [US6] Update frontend deployment with Dapr sidecar annotations in `helm/todo-chatbot/templates/frontend-deployment.yaml`
  - **Purpose**: Enable Dapr sidecar on frontend for service invocation
  - **Input**: plan.md frontend-deployment.yaml updates
  - **Tool**: Helm / Claude Code
  - **Expected output**: Frontend Deployment with Dapr annotations

- [ ] T042 [US6] Extend ConfigMap with Dapr configuration in `helm/todo-chatbot/templates/configmap.yaml`
  - **Purpose**: Add Dapr-related environment variables to the shared ConfigMap
  - **Input**: T002 config vars, plan.md configmap.yaml updates
  - **Tool**: Helm / Claude Code
  - **Expected output**: ConfigMap includes `DAPR_PUBSUB_NAME`, `DAPR_HTTP_PORT` values

- [ ] T043 [US6] Create local Helm values override in `helm/todo-chatbot/values-local.yaml`
  - **Purpose**: Minikube-specific configuration (Strimzi broker address, NodePort, local image refs, resource limits)
  - **Input**: plan.md Local Deployment table, quickstart.md steps
  - **Tool**: Helm / Claude Code
  - **Expected output**: `values-local.yaml` with Kafka broker `todo-kafka-kafka-bootstrap:9092`, service type NodePort, imagePullPolicy Never, reduced resource limits

- [ ] T044 [US6] Update `helm/todo-chatbot/values.yaml` with Dapr and Kafka defaults
  - **Purpose**: Add default values for Dapr, Kafka, and event-driven configuration
  - **Input**: plan.md values.yaml updates
  - **Tool**: Helm / Claude Code
  - **Expected output**: `values.yaml` with dapr.enabled, kafka.brokers, kafka.topics, event schema version defaults

- [ ] T045 [US6] Update backend Dockerfile for Dapr compatibility in `backend/Dockerfile`
  - **Purpose**: Ensure backend container exposes app port and is compatible with Dapr sidecar injection
  - **Input**: plan.md Dockerfile updates
  - **Tool**: Claude Code
  - **Expected output**: Dockerfile exposes port 8000, runs with `--host 0.0.0.0`, includes health check endpoint

- [ ] T046 [US6] Update `helm/todo-chatbot/templates/NOTES.txt` with Dapr and Kafka post-install info
  - **Purpose**: Provide users with post-install verification commands
  - **Input**: quickstart.md Step 8 verification commands
  - **Tool**: Helm / Claude Code
  - **Expected output**: NOTES.txt includes commands to check Dapr status, Kafka topics, and access frontend

- [ ] T047 [US6] Run `helm lint` validation on updated chart
  - **Purpose**: Validate Helm chart syntax before deployment
  - **Input**: All Helm template files (T035–T046)
  - **Tool**: Helm
  - **Expected output**: `helm lint helm/todo-chatbot/` passes with no errors

**Checkpoint**: US6 complete — full system deployable on Minikube with Dapr + Kafka.

---

## Phase 9: User Story 7 — Cloud Kubernetes Deployment (Priority: P7)

**Goal**: Deploy the same system to a production cloud Kubernetes cluster (AKS/GKE/OKE) using environment-specific Helm values.

**Independent Test**: `helm install` with production values on cloud cluster → all pods Running → end-to-end task flow works.

### Implementation for User Story 7

- [ ] T048 [P] [US7] Create production Helm values in `helm/todo-chatbot/values-production.yaml`
  - **Purpose**: Cloud-specific overrides for managed Kafka, container registry, resource limits, replica counts, LoadBalancer
  - **Input**: plan.md Production Deployment table, research.md R9 (cloud provider isolation)
  - **Tool**: Helm / Claude Code
  - **Expected output**: `values-production.yaml` with managed Kafka broker address placeholder, GHCR image registry, higher resource limits, replica count 2+, service type LoadBalancer

- [ ] T049 [P] [US7] Add imagePullSecrets support to Helm templates in `helm/todo-chatbot/templates/backend-deployment.yaml` and `frontend-deployment.yaml`
  - **Purpose**: Enable pulling images from private container registries in cloud environments
  - **Input**: quickstart.md Troubleshooting (image pull errors)
  - **Tool**: Helm / Claude Code
  - **Expected output**: Deployments conditionally include `imagePullSecrets` when `values.imagePullSecrets` is set

- [ ] T050 [US7] Add Ingress template in `helm/todo-chatbot/templates/ingress.yaml`
  - **Purpose**: Provide cloud ingress resource for external access (alternative to LoadBalancer)
  - **Input**: plan.md Production: LoadBalancer or Ingress
  - **Tool**: Helm / Claude Code
  - **Expected output**: Optional Ingress resource (enabled via `values.ingress.enabled`), supporting annotations for cloud-specific ingress controllers

- [ ] T051 [US7] Validate chart portability: `helm template` with both local and production values
  - **Purpose**: Verify the same chart renders correctly for both environments with no template errors
  - **Input**: values-local.yaml (T043), values-production.yaml (T048)
  - **Tool**: Helm
  - **Expected output**: `helm template` succeeds for both values files; diff shows only expected differences (broker address, registry, resources, service type)

**Checkpoint**: US7 complete — same Helm chart deploys to both local and cloud clusters.

---

## Phase 10: User Story 8 — CI/CD Pipeline (Priority: P8)

**Goal**: Automated GitHub Actions workflows for CI (lint, test, build, push) and CD (deploy via Helm) with secret management.

**Independent Test**: Push commit to main → CI workflow runs successfully → images tagged and pushed → CD deploys via Helm.

### Implementation for User Story 8

- [ ] T052 [P] [US8] Create CI workflow in `.github/workflows/ci.yaml`
  - **Purpose**: Automated lint, test, build, and push pipeline triggered on push/PR to main
  - **Input**: plan.md CI Workflow definition, spec.md FR-024
  - **Tool**: Claude Code
  - **Expected output**: GitHub Actions workflow with steps: checkout, setup Python 3.12 + Node.js 18, install deps, ruff lint, pytest, npm ci + eslint + next build, docker build + tag (SHA + semver), push to GHCR, helm lint

- [ ] T053 [P] [US8] Create CD staging workflow in `.github/workflows/cd-staging.yaml`
  - **Purpose**: Deploy to staging environment on CI success
  - **Input**: plan.md CD Workflow, spec.md FR-025
  - **Tool**: Claude Code
  - **Expected output**: GitHub Actions workflow triggered on CI completion: configure kubectl, helm upgrade --install with staging values, wait for rollout, smoke test health endpoints, rollback on failure

- [ ] T054 [P] [US8] Create CD production workflow in `.github/workflows/cd-production.yaml`
  - **Purpose**: Deploy to production environment on tag creation (v*)
  - **Input**: plan.md CD Workflow, spec.md FR-025
  - **Tool**: Claude Code
  - **Expected output**: GitHub Actions workflow triggered on tag `v*`: configure kubectl from GH secret, helm upgrade --install with values-production.yaml, wait for rollout, smoke test, rollback + notify on failure

- [ ] T055 [US8] Document required GitHub Actions secrets in `.github/workflows/README.md`
  - **Purpose**: List all secrets required for CI/CD workflows so engineers can configure the repository
  - **Input**: spec.md FR-026 (secrets management), plan.md CI/CD architecture
  - **Tool**: Claude Code
  - **Expected output**: README documenting secrets: KUBECONFIG, GHCR_TOKEN, DATABASE_URL, OPENAI_API_KEY, BETTER_AUTH_SECRET, GROQ_API_KEY

- [ ] T056 [US8] Validate CI workflow YAML syntax
  - **Purpose**: Ensure GitHub Actions workflow files are valid YAML and use correct action versions
  - **Input**: T052, T053, T054 workflow files
  - **Tool**: Claude Code
  - **Expected output**: All workflow files pass YAML validation; action versions pinned to specific SHA or major version

**Checkpoint**: US8 complete — CI/CD pipeline automates build, test, and deployment.

---

## Phase 11: Observability & Health Checks

**Purpose**: Ensure all services expose health/readiness endpoints and logs are structured for kubectl access.

- [ ] T057 [P] Extend backend health check to include Dapr sidecar status in `backend/src/api/v1/health.py`
  - **Purpose**: Readiness check should verify Dapr sidecar is healthy (spec.md FR-030)
  - **Input**: spec.md FR-028 (/health, /ready), FR-030 (Dapr sidecar health)
  - **Tool**: Claude Code
  - **Expected output**: `/ready` endpoint checks Dapr sidecar health via `http://localhost:3500/v1.0/healthz`; `/health` returns basic liveness

- [ ] T058 [P] Add structured logging for event operations in `backend/src/services/event_publisher.py`
  - **Purpose**: Ensure all event publishes and failures are logged to stdout for kubectl access (FR-027)
  - **Input**: spec.md FR-027, FR-029
  - **Tool**: Claude Code
  - **Expected output**: Structured JSON logs for: event published (topic, event_id, type), event publish failed (error, topic), consumer processing (event_id, status)

---

## Phase 12: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, documentation updates, and cross-story integration verification.

- [ ] T059 [P] Update `helm/todo-chatbot/templates/_helpers.tpl` with new helper functions
  - **Purpose**: Add template helpers for Dapr annotations, Kafka config rendering
  - **Input**: T040, T041 Dapr annotation patterns
  - **Tool**: Helm / Claude Code
  - **Expected output**: Helper templates for `dapr.annotations`, `kafka.brokerUrl` reducing duplication across templates

- [ ] T060 Run quickstart.md validation (end-to-end local deployment test)
  - **Purpose**: Verify the full quickstart workflow from Step 1 through Step 8
  - **Input**: quickstart.md all steps
  - **Tool**: kubectl / Helm / Dapr CLI
  - **Expected output**: All pods Running, Dapr sidecars healthy, events flowing, frontend accessible, task CRUD triggers events

- [ ] T061 Validate all Dapr components with `dapr components -k`
  - **Purpose**: Verify Dapr recognizes all registered components
  - **Input**: T036, T037, T038, T039 Dapr manifests
  - **Tool**: Dapr CLI
  - **Expected output**: `dapr components -k` lists pubsub-kafka, secrets-kubernetes; all components in "Running" state

- [ ] T062 Run `helm upgrade --dry-run` to validate rolling update behavior
  - **Purpose**: Verify Helm upgrade path works without breaking existing deployment
  - **Input**: All Helm templates
  - **Tool**: Helm / kubectl
  - **Expected output**: Dry-run succeeds, shows expected diff with no breaking changes

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 — BLOCKS all user stories
- **Phase 3 (US1)**: Depends on Phase 2 — MVP milestone
- **Phase 4 (US2)**: Depends on Phase 2 only — can run in parallel with US1
- **Phase 5 (US3)**: Depends on Phase 2 + US1 (needs event publishing for reminder suppression)
- **Phase 6 (US4)**: Depends on Phase 2 + US1 (needs `task.completed` events)
- **Phase 7 (US5)**: Depends on Phase 2 + US1 (needs events to consume for audit)
- **Phase 8 (US6)**: Depends on Phase 2 + all backend code (US1–US5 for full deployment)
- **Phase 9 (US7)**: Depends on US6 (local deployment validated first)
- **Phase 10 (US8)**: Depends on US6 + US7 (deployments validated before automating)
- **Phase 11 (Observability)**: Can run in parallel with US3–US5
- **Phase 12 (Polish)**: Depends on all preceding phases

### User Story Dependencies

```
Phase 1 (Setup)
  └── Phase 2 (Foundational)
        ├── US1 (P1, MVP) ◄── CRITICAL PATH
        │     ├── US3 (P3, Reminders) — needs events for suppression
        │     ├── US4 (P4, Recurring) — needs task.completed events
        │     └── US5 (P5, Audit Log) — needs events to consume
        ├── US2 (P2, Search/Filter) — independent of US1
        │
        └── US6 (P6, Local K8s) — needs all backend code
              └── US7 (P7, Cloud K8s) — needs local validated
                    └── US8 (P8, CI/CD) — needs deployments validated
```

### Parallel Opportunities

**Within Phase 1**: T003, T004, T005 can run in parallel (different files)
**Within Phase 8 (US6)**: T035, T036, T037, T038, T039 can run in parallel (different Helm templates)
**Within Phase 9 (US7)**: T048, T049 can run in parallel
**Within Phase 10 (US8)**: T052, T053, T054 can run in parallel (different workflow files)
**Cross-story**: US2 can run in parallel with US1 (no dependency)
**Cross-story**: Phase 11 (Observability) can run in parallel with US3–US5

---

## Parallel Example: User Story 6 (Local K8s)

```bash
# Launch all Dapr component templates in parallel:
Task: "Create Dapr Pub/Sub component in helm/todo-chatbot/templates/dapr-pubsub.yaml"
Task: "Create Dapr subscription manifest in helm/todo-chatbot/templates/dapr-subscription.yaml"
Task: "Create Dapr resiliency policy in helm/todo-chatbot/templates/dapr-resiliency.yaml"
Task: "Create Dapr secrets component in helm/todo-chatbot/templates/dapr-secrets.yaml"

# Then sequentially:
Task: "Update backend deployment with Dapr annotations"
Task: "Update frontend deployment with Dapr annotations"
Task: "Run helm lint validation"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001–T006)
2. Complete Phase 2: Foundational event infrastructure (T007–T010)
3. Complete Phase 3: US1 — Event-driven task operations (T011–T016)
4. **STOP and VALIDATE**: Create/update/complete/delete tasks → verify events on Kafka
5. This delivers the event-driven backbone that all other stories build on

### Incremental Delivery

1. Setup + Foundational → Event infrastructure ready
2. US1 (Events) → Validate events flow → **MVP!**
3. US2 (Search/Filter) → Validate search works → Deploy/Demo
4. US3 (Reminders) + US4 (Recurring) + US5 (Audit) → Validate all consumers → Deploy/Demo
5. US6 (Local K8s) → Validate Minikube deployment → Demo
6. US7 (Cloud K8s) → Validate cloud deployment → Demo
7. US8 (CI/CD) → Validate automation → Production-ready!

### Suggested MVP Scope

**MVP = Phase 1 + Phase 2 + Phase 3 (US1)**
- 16 tasks (T001–T016)
- Delivers: Event-driven task operations with Dapr Pub/Sub on Kafka
- Independently testable and demonstrable

---

## Summary

| Metric | Value |
|--------|-------|
| **Total tasks** | 62 |
| **Phase 1 (Setup)** | 6 tasks |
| **Phase 2 (Foundational)** | 4 tasks |
| **US1 (Events, P1)** | 6 tasks |
| **US2 (Search, P2)** | 3 tasks |
| **US3 (Reminders, P3)** | 7 tasks |
| **US4 (Recurring, P4)** | 3 tasks |
| **US5 (Audit, P5)** | 5 tasks |
| **US6 (Local K8s, P6)** | 13 tasks |
| **US7 (Cloud K8s, P7)** | 4 tasks |
| **US8 (CI/CD, P8)** | 5 tasks |
| **Observability** | 2 tasks |
| **Polish** | 4 tasks |
| **Parallel opportunities** | 18 tasks marked [P] |
| **MVP scope** | T001–T016 (16 tasks) |

---

## Notes

- [P] tasks = different files, no dependencies — can execute concurrently
- [Story] label maps task to specific user story for traceability
- Each task includes Purpose, Input, Tool, and Expected Output per user request
- All Kafka interaction via Dapr only (no Kafka SDK in app code) per constitution XIV
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
