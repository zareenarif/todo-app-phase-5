# Implementation Plan: Cloud-Native Event-Driven Todo AI Chatbot

**Branch**: `010-cloud-native-deployment` | **Date**: 2026-02-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/010-cloud-native-deployment/spec.md`

## Summary

Transform the Phase 4 local Kubernetes deployment into a production-grade, event-driven, cloud-native system. The plan introduces Kafka as the event backbone (abstracted via Dapr Pub/Sub), extends MCP tools with search/filter/sort/reminders, adds recurring task generation and audit logging via event consumers, deploys to both local Minikube and cloud Kubernetes (AKS/GKE/OKE), and automates the full build-test-deploy lifecycle via GitHub Actions CI/CD pipelines.

## Technical Context

**Language/Version**: Python 3.12 (backend), Node.js 18 / TypeScript (frontend)
**Primary Dependencies**: FastAPI, SQLModel, Dapr Python SDK, OpenAI Agents SDK, MCP SDK, Next.js 14
**Storage**: Neon Serverless PostgreSQL (external, via SQLModel ORM), Kafka (event store)
**Testing**: pytest (backend), helm lint + kubectl dry-run (infrastructure)
**Target Platform**: Kubernetes — Minikube (local), AKS/GKE/OKE (production)
**Project Type**: Web application (frontend + backend + infrastructure)
**Performance Goals**: Event publish <2s after DB write, search <3s over 1000+ tasks, reminder accuracy within 60s
**Constraints**: All Kafka interaction via Dapr only (no Kafka SDK in app), cloud-neutral (no provider-specific code), all infra AI-generated
**Scale/Scope**: Horizontal scaling via Kubernetes Deployments, Kafka partitioning for throughput

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| # | Principle | Status | Evidence |
|---|-----------|--------|----------|
| I | Specification Before Implementation | PASS | spec.md approved with 33 FRs, 8 user stories |
| II | Planning Before Coding | PASS | This plan document |
| III | Tasks Before Execution | PENDING | tasks.md to be generated via /sp.tasks |
| IV | Simplicity Over Complexity | PASS | Dapr abstracts Kafka; standard K8s objects only |
| V | Scope Discipline | PASS | Out-of-scope items defined in constitution + spec |
| VI | Security by Design | PASS | Secrets via K8s Secrets + GitHub Actions secrets; Dapr component scoping; no hardcoded secrets |
| VII | Stateless Services | PASS | All services stateless; event processing idempotent; state in external DB |
| VIII | MCP Tool Discipline | PASS | MCP tools extended (search/filter/sort/reminders); still single-responsibility, stateless |
| IX | Conversation State Persistence | PASS | Preserved unchanged from Phase 3 |
| X | AI Agent Boundary Discipline | PASS | Agent boundaries preserved; Dapr layer is infrastructure, not agent logic |
| XI | AI-Generated Infrastructure Only | PASS | Claude Code generates all Helm, Dapr, Kafka, CI/CD configs |
| XII | Helm as Single Source of Truth | PASS | All K8s resources including Dapr components defined in Helm chart |
| XIII | Observable and Resilient Deployment | PASS | Health checks, Dapr sidecar health, Kafka consumer lag monitoring |
| XIV | Event-Driven Architecture via Dapr | PASS | Kafka backbone, Dapr Pub/Sub abstraction, dead letter topics, idempotent consumers |
| XV | Cloud Neutrality | PASS | No cloud-specific code in app; provider differences isolated to values files |
| XVI | Automated CI/CD Pipeline | PASS | GitHub Actions CI + CD workflows defined |

**Gate Result: PASS** — No violations. Proceed to Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/010-cloud-native-deployment/
├── plan.md              # This file
├── research.md          # Phase 0: technology decisions
├── data-model.md        # Phase 1: entity definitions
├── quickstart.md        # Phase 1: developer setup guide
├── contracts/           # Phase 1: API contracts
│   ├── task-events.yaml     # Event schema contracts
│   ├── reminders-api.yaml   # Reminder endpoint contracts
│   └── search-api.yaml      # Search/filter/sort contracts
├── checklists/
│   └── requirements.md # Spec quality checklist
└── tasks.md             # Phase 2 output (/sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── api/v1/
│   │   ├── tasks.py         # Extended: search/filter/sort params
│   │   ├── reminders.py     # NEW: reminder CRUD endpoints
│   │   ├── audit.py         # NEW: audit log query endpoints
│   │   └── chat.py          # Preserved from Phase 3
│   ├── models/
│   │   ├── task.py          # Preserved (priority, due_date, recurrence, tags exist)
│   │   ├── reminder.py      # NEW: Reminder entity
│   │   └── audit_log.py     # NEW: AuditLogEntry entity
│   ├── schemas/
│   │   ├── task.py          # Extended: search/filter query params
│   │   ├── reminder.py      # NEW: reminder request/response schemas
│   │   ├── audit.py         # NEW: audit log response schema
│   │   └── events.py        # NEW: event envelope schema
│   ├── services/
│   │   ├── event_publisher.py   # NEW: Dapr Pub/Sub publishing service
│   │   ├── reminder_service.py  # NEW: reminder scheduling via Dapr Jobs
│   │   ├── recurrence_service.py # NEW: recurring task generation
│   │   └── audit_service.py     # NEW: audit log consumer
│   ├── events/
│   │   ├── handlers.py      # NEW: Dapr subscription event handlers
│   │   └── schemas.py       # NEW: event envelope definitions
│   ├── mcp/
│   │   ├── tools.py         # Extended: search/filter/sort + reminders
│   │   └── server.py        # Preserved from Phase 3
│   └── core/
│       ├── database.py      # Preserved
│       └── config.py        # Extended: Dapr config vars
├── alembic/
│   └── versions/            # NEW: migration for reminder + audit_log tables
├── requirements.txt         # Extended: dapr, dapr-ext-fastapi
└── Dockerfile               # Updated: Dapr sidecar-compatible

frontend/
├── src/                     # Preserved from Phase 4 (no changes required)
└── Dockerfile               # Preserved from Phase 4

helm/todo-chatbot/
├── Chart.yaml               # Updated: version 2.0.0, Kafka dependency
├── values.yaml              # Updated: Dapr, Kafka, multi-env defaults
├── values-local.yaml        # NEW: Minikube-specific overrides
├── values-production.yaml   # NEW: Cloud Kubernetes overrides
├── templates/
│   ├── _helpers.tpl         # Preserved + extended
│   ├── NOTES.txt            # Updated: Dapr + Kafka post-install info
│   ├── frontend-deployment.yaml  # Updated: Dapr sidecar annotations
│   ├── frontend-service.yaml     # Preserved
│   ├── backend-deployment.yaml   # Updated: Dapr sidecar annotations
│   ├── backend-service.yaml      # Preserved
│   ├── configmap.yaml            # Extended: Dapr config vars
│   ├── dapr-pubsub.yaml          # NEW: Dapr Pub/Sub component (Kafka)
│   ├── dapr-subscription.yaml    # NEW: Dapr topic subscriptions
│   ├── dapr-resiliency.yaml      # NEW: Dapr resiliency policy
│   └── dapr-secrets.yaml         # NEW: Dapr secrets component
└── .helmignore

.github/workflows/
├── ci.yaml                  # NEW: lint, test, build, push
├── cd-staging.yaml          # NEW: deploy to staging
└── cd-production.yaml       # NEW: deploy to production
```

**Structure Decision**: Web application structure (frontend + backend) preserved from Phase 4. Infrastructure layer extended with Dapr components, Kafka dependency, CI/CD workflows, and multi-environment Helm values. Backend extended with event publishing, reminders, recurrence, and audit services. Frontend unchanged.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Kafka StatefulSet in cluster | Event backbone for async processing | In-memory queues rejected: not persistent, not scalable, no replay |
| Dapr sidecar on all pods | Abstracts Kafka + provides resiliency | Direct Kafka SDK rejected: violates constitution principle XIV, creates cloud lock-in |
| 3 CI/CD workflows | Separation of CI, staging CD, production CD | Single workflow rejected: staging and production need different approval gates |

## Architecture: Event Flow

### Event Publishing Flow

```
User Action → MCP Tool / API Endpoint
  → Database Write (SQLModel + PostgreSQL)
  → Event Publisher Service
  → Dapr Sidecar (HTTP POST /v1.0/publish/pubsub-kafka/<topic>)
  → Kafka Broker
  → Topic: todo.task-events | todo.reminders | todo.task-updates
```

### Event Consumption Flow

```
Kafka Topic → Dapr Sidecar (subscription delivery)
  → Backend Event Handler Endpoint (POST /events/<topic>)
  → Service Layer (audit_service | recurrence_service | reminder_service)
  → Database Write (if applicable)
```

### Subscription Routes

| Topic | Handler | Service | Action |
|-------|---------|---------|--------|
| `todo.task-events` | `/events/task-events` | `audit_service` | Write audit log entry |
| `todo.task-events` (type=`task.completed`) | `/events/task-events` | `recurrence_service` | Generate next recurring task instance |
| `todo.reminders` | `/events/reminders` | `reminder_service` | Log reminder delivery |
| `todo.task-updates` | `/events/task-updates` | `audit_service` | Write audit log entry for updates |

### Dead Letter Handling

| Source Topic | DLQ Topic | Trigger |
|-------------|-----------|---------|
| `todo.task-events` | `todo.task-events.dlq` | 3 retries exhausted |
| `todo.reminders` | `todo.reminders.dlq` | 3 retries exhausted |
| `todo.task-updates` | `todo.task-updates.dlq` | 3 retries exhausted |

## Architecture: Dapr Building Blocks

| Building Block | Component | Backend | Purpose |
|----------------|-----------|---------|---------|
| Pub/Sub | `pubsub-kafka` | Kafka (Strimzi local / managed cloud) | Event publishing and subscription |
| Secrets | `secrets-kubernetes` | Kubernetes Secrets | Secret retrieval via Dapr API |
| Resiliency | `resiliency-policy` | N/A | Retry + circuit breaker for pub/sub |

**Dapr Jobs API**: Used for scheduled reminder delivery. The backend registers a job via the Dapr Jobs API with the remind_at timestamp. When the job fires, it publishes a `reminder.triggered` event to the `todo.reminders` topic.

## Architecture: Deployment Environments

### Local (Minikube)

| Component | Configuration |
|-----------|--------------|
| Kubernetes | Minikube |
| Kafka | Strimzi Kafka operator (single-node) |
| Dapr | dapr init -k (Helm install) |
| Images | Local build, `minikube image load` |
| Frontend Service | NodePort |
| Backend Service | ClusterIP |
| Secrets | kubectl create secret |
| Values file | `values-local.yaml` |

### Production (Cloud)

| Component | Configuration |
|-----------|--------------|
| Kubernetes | AKS / GKE / OKE |
| Kafka | Redpanda Cloud or Confluent Cloud (managed) |
| Dapr | dapr init -k (Helm install on cloud cluster) |
| Images | Container registry (GHCR / ACR / GCR / OCIR) |
| Frontend Service | LoadBalancer or Ingress |
| Backend Service | ClusterIP |
| Secrets | kubectl create secret (from CI/CD) |
| Values file | `values-production.yaml` |

## Architecture: CI/CD Pipeline

### CI Workflow (`.github/workflows/ci.yaml`)

```
Trigger: push to main, pull_request to main

Steps:
1. Checkout code
2. Setup Python 3.12, Node.js 18
3. Install backend dependencies
4. Run backend linting (ruff)
5. Run backend tests (pytest)
6. Install frontend dependencies (npm ci)
7. Run frontend linting (eslint)
8. Run frontend build (next build)
9. Build Docker images (backend + frontend)
10. Tag images: ${{ github.sha }} + semantic version
11. Push images to container registry
12. Run helm lint
```

### CD Workflow (`.github/workflows/cd-production.yaml`)

```
Trigger: on CI success + tag creation (v*)

Steps:
1. Checkout code
2. Configure kubectl (kubeconfig from GitHub secret)
3. Helm upgrade --install with values-production.yaml
4. Wait for rollout status
5. Run smoke tests (health check endpoints)
6. On failure: helm rollback + notify
```

## Architecture: Search, Filter, Sort

### Extended Query Parameters (list_tasks)

| Parameter | Type | Description |
|-----------|------|-------------|
| `search` | string | Keyword search across title + description (ILIKE) |
| `status` | enum | Filter: "pending" or "completed" |
| `priority` | enum | Filter: "high", "medium", "low" |
| `tags` | string | Comma-separated tag filter (any match) |
| `due_date_from` | date | Filter: due date >= value |
| `due_date_to` | date | Filter: due date <= value |
| `sort` | enum | Sort field: "created_at", "due_date", "priority", "title" |
| `order` | enum | Sort direction: "asc" or "desc" |

These parameters apply to both the REST API endpoint (`GET /api/v1/tasks`) and the MCP `list_tasks` tool.

## Architecture: Reminder System

### Flow

```
1. User sets reminder (MCP tool or API: set_reminder)
2. Reminder entity saved to database (status: PENDING)
3. Dapr Job registered with remind_at timestamp
4. At remind_at: Dapr Job fires → publishes reminder.triggered to todo.reminders
5. Reminder handler updates status to TRIGGERED
6. If task already completed/deleted: reminder suppressed (status: CANCELLED)
```

### Reminder Lead Times

| Option | Value |
|--------|-------|
| 15 minutes before | `remind_at = due_date - 15min` |
| 30 minutes before | `remind_at = due_date - 30min` |
| 1 hour before | `remind_at = due_date - 1h` |
| 1 day before | `remind_at = due_date - 1d` |

## Architecture: Recurring Task Generation

### Flow

```
1. User completes a task with recurrence set (DAILY/WEEKLY/MONTHLY)
2. task.completed event published to todo.task-events
3. Recurrence handler receives event, checks recurrence field
4. If recurrence is set:
   a. Calculate next due_date based on pattern
   b. Create new Task via database (preserving title, description, priority, tags, recurrence)
   c. Publish task.created event for the new instance
5. If recurrence is not set: no action
```

### Due Date Calculation

| Pattern | Calculation |
|---------|-------------|
| DAILY | `original_due_date + 1 day` |
| WEEKLY | `original_due_date + 7 days` |
| MONTHLY | `original_due_date + 1 calendar month` (dateutil.relativedelta) |

## Post-Design Constitution Re-Check

| # | Principle | Status | Notes |
|---|-----------|--------|-------|
| I–III | SDD Workflow | PASS | Spec → Plan → Tasks pipeline followed |
| IV | Simplicity | PASS | Standard patterns: Dapr SDK, Helm, GitHub Actions |
| V | Scope | PASS | No feature creep; all changes traced to spec FRs |
| VI | Security | PASS | Secrets in K8s Secrets + GH Actions; Dapr scoped |
| VII | Stateless | PASS | All services stateless; idempotent event processing |
| VIII | MCP | PASS | MCP tools extended, not replaced; single-responsibility |
| IX | Conversations | PASS | Unchanged |
| X | Agent Boundaries | PASS | Agent unaware of Dapr/Kafka infrastructure |
| XI | AI-Generated | PASS | All infra to be generated by Claude Code |
| XII | Helm SSOT | PASS | All resources in Helm chart; multi-env values |
| XIII | Observable | PASS | Health checks, Dapr dashboard, Kafka lag |
| XIV | Event-Driven | PASS | Kafka + Dapr Pub/Sub + DLQ + idempotent consumers |
| XV | Cloud Neutral | PASS | Provider differences in values files only |
| XVI | CI/CD | PASS | GitHub Actions CI + CD defined |

**Post-Design Gate: PASS**
