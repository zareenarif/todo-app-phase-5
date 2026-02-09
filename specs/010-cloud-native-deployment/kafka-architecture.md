# Kafka Architecture: Phase V — Cloud-Native Event-Driven Todo AI Chatbot

**Branch**: `010-cloud-native-deployment` | **Date**: 2026-02-09
**Input**: plan.md, spec.md, research.md, contracts/task-events.yaml, contracts/reminders-api.yaml

---

## 1. Topic Definitions

### Primary Topics

| Topic | Partitions | Replication | Retention | Purpose |
|-------|-----------|-------------|-----------|---------|
| `todo.task-events` | 3 | Local: 1 / Cloud: 3 | 7 days | Task lifecycle events: created, completed, deleted |
| `todo.task-updates` | 3 | Local: 1 / Cloud: 3 | 7 days | Task field-level updates |
| `todo.reminders` | 1 | Local: 1 / Cloud: 3 | 3 days | Reminder trigger events |

### Dead Letter Topics (DLQ)

| Topic | Partitions | Replication | Retention | Purpose |
|-------|-----------|-------------|-----------|---------|
| `todo.task-events.dlq` | 1 | Local: 1 / Cloud: 3 | 30 days | Unprocessable task events after retry exhaustion |
| `todo.task-updates.dlq` | 1 | Local: 1 / Cloud: 3 | 30 days | Unprocessable task update events |
| `todo.reminders.dlq` | 1 | Local: 1 / Cloud: 3 | 30 days | Unprocessable reminder events |

### Partitioning Strategy

- **Partition key**: `user_id` (ensures all events for a user land on the same partition for ordering)
- **`todo.task-events`**: 3 partitions for consumer parallelism (audit + recurrence)
- **`todo.task-updates`**: 3 partitions for audit consumer throughput
- **`todo.reminders`**: 1 partition (low volume, ordering not critical)

---

## 2. Producers and Consumers

### Producers

```
┌─────────────────────────────────────────────────────────────────┐
│                        PRODUCERS                                 │
├──────────────────┬────────────────────┬─────────────────────────┤
│ Producer         │ Topics             │ Trigger                  │
├──────────────────┼────────────────────┼─────────────────────────┤
│ EventPublisher   │ todo.task-events   │ Task create/complete/    │
│ Service          │                    │ delete via API or MCP    │
│ (todo-backend)   │                    │                          │
│                  ├────────────────────┼─────────────────────────┤
│                  │ todo.task-updates  │ Task field update via    │
│                  │                    │ API or MCP               │
├──────────────────┼────────────────────┼─────────────────────────┤
│ Dapr Jobs        │ todo.reminders     │ Scheduled reminder time  │
│ Scheduler        │                    │ arrives (remind_at)      │
├──────────────────┼────────────────────┼─────────────────────────┤
│ Recurrence       │ todo.task-events   │ New task instance created│
│ Service          │                    │ (task.created event)     │
│ (todo-backend)   │                    │                          │
└──────────────────┴────────────────────┴─────────────────────────┘
```

### Consumers

```
┌─────────────────────────────────────────────────────────────────┐
│                        CONSUMERS                                 │
├──────────────────┬────────────────────┬─────────────────────────┤
│ Consumer         │ Topics             │ Action                   │
├──────────────────┼────────────────────┼─────────────────────────┤
│ Audit Service    │ todo.task-events   │ Write AuditLogEntry      │
│                  │ todo.task-updates  │ (idempotent via          │
│                  │                    │ event_id dedup)          │
├──────────────────┼────────────────────┼─────────────────────────┤
│ Recurrence       │ todo.task-events   │ On task.completed:       │
│ Service          │ (type=task.        │ generate next recurring  │
│                  │  completed)        │ task if recurrence set   │
├──────────────────┼────────────────────┼─────────────────────────┤
│ Reminder         │ todo.reminders     │ Update reminder status   │
│ Service          │                    │ to TRIGGERED; suppress   │
│                  │                    │ if task completed/       │
│                  │                    │ deleted                  │
├──────────────────┼────────────────────┼─────────────────────────┤
│ Reminder         │ todo.task-events   │ On task.completed or     │
│ Suppression      │ (type=task.        │ task.deleted: cancel     │
│                  │  completed |       │ pending reminders        │
│                  │  task.deleted)     │                          │
└──────────────────┴────────────────────┴─────────────────────────┘
```

### Consumer Groups

| Consumer Group | Consumer | Topics | Concurrency |
|---------------|----------|--------|-------------|
| `audit-consumer` | AuditService | todo.task-events, todo.task-updates | 1 per partition |
| `recurrence-consumer` | RecurrenceService | todo.task-events | 1 per partition |
| `reminder-consumer` | ReminderService | todo.reminders | 1 (single partition) |
| `reminder-suppression` | ReminderService | todo.task-events | 1 per partition |

---

## 3. Event Schemas (CloudEvents-compatible)

### Event Envelope

All events follow the CloudEvents specification subset:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "source": "todo-backend",
  "type": "task.created",
  "time": "2026-02-09T14:30:00Z",
  "data": { ... }
}
```

### task.created

```json
{
  "id": "uuid-v4",
  "source": "todo-backend",
  "type": "task.created",
  "time": "2026-02-09T14:30:00Z",
  "data": {
    "task_id": "uuid-v4",
    "user_id": "uuid-v4",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "priority": "high",
    "tags": ["personal", "errands"],
    "due_date": "2026-02-10",
    "recurrence": "weekly",
    "created_at": "2026-02-09T14:30:00Z"
  }
}
```

**Topic**: `todo.task-events` | **Partition key**: `data.user_id`

### task.updated

```json
{
  "id": "uuid-v4",
  "source": "todo-backend",
  "type": "task.updated",
  "time": "2026-02-09T15:00:00Z",
  "data": {
    "task_id": "uuid-v4",
    "user_id": "uuid-v4",
    "changes": {
      "title": "Buy groceries and supplies",
      "priority": "medium"
    },
    "updated_at": "2026-02-09T15:00:00Z"
  }
}
```

**Topic**: `todo.task-updates` | **Partition key**: `data.user_id`

### task.completed

```json
{
  "id": "uuid-v4",
  "source": "todo-backend",
  "type": "task.completed",
  "time": "2026-02-09T16:00:00Z",
  "data": {
    "task_id": "uuid-v4",
    "user_id": "uuid-v4",
    "title": "Buy groceries",
    "recurrence": "weekly",
    "due_date": "2026-02-10",
    "completed_at": "2026-02-09T16:00:00Z"
  }
}
```

**Topic**: `todo.task-events` | **Partition key**: `data.user_id`
**Consumers**: AuditService (log entry), RecurrenceService (if recurrence set, generate next task)

### task.deleted

```json
{
  "id": "uuid-v4",
  "source": "todo-backend",
  "type": "task.deleted",
  "time": "2026-02-09T17:00:00Z",
  "data": {
    "task_id": "uuid-v4",
    "user_id": "uuid-v4",
    "title": "Buy groceries",
    "deleted_at": "2026-02-09T17:00:00Z"
  }
}
```

**Topic**: `todo.task-events` | **Partition key**: `data.user_id`
**Consumers**: AuditService (log entry), ReminderSuppression (cancel pending reminders)

### reminder.triggered

```json
{
  "id": "uuid-v4",
  "source": "todo-reminder-scheduler",
  "type": "reminder.triggered",
  "time": "2026-02-10T09:30:00Z",
  "data": {
    "reminder_id": "uuid-v4",
    "task_id": "uuid-v4",
    "user_id": "uuid-v4",
    "task_title": "Buy groceries",
    "due_date": "2026-02-10"
  }
}
```

**Topic**: `todo.reminders` | **Partition key**: `data.user_id`

---

## 4. Event Flow Diagrams

### 4.1 Complete Event Flow — All Topics

```
                              ┌─────────────────┐
                              │   User / Chat    │
                              │   (Frontend)     │
                              └────────┬─────────┘
                                       │ HTTP
                                       ▼
                         ┌─────────────────────────────┐
                         │     FastAPI Backend          │
                         │  ┌──────────┐ ┌───────────┐ │
                         │  │ REST API │ │ MCP Tools │ │
                         │  └────┬─────┘ └─────┬─────┘ │
                         │       │              │       │
                         │       ▼              ▼       │
                         │  ┌────────────────────────┐  │
                         │  │   Task Service Layer   │  │
                         │  │   (DB Write First)     │  │
                         │  └───────────┬────────────┘  │
                         │              │               │
                         │              ▼               │
                         │  ┌────────────────────────┐  │
                         │  │  EventPublisherService  │  │
                         │  │  (fire-and-forget)      │  │
                         │  └───────────┬────────────┘  │
                         └──────────────┼───────────────┘
                                        │ Dapr HTTP API
                                        ▼
                         ┌─────────────────────────────┐
                         │      Dapr Sidecar            │
                         │  POST /v1.0/publish/         │
                         │  pubsub-kafka/<topic>        │
                         └──────────────┬───────────────┘
                                        │
              ┌─────────────────────────┼────────────────────────┐
              │                         │                        │
              ▼                         ▼                        ▼
   ┌──────────────────┐   ┌───────────────────┐   ┌──────────────────┐
   │ todo.task-events │   │ todo.task-updates │   │  todo.reminders  │
   │ (Kafka Topic)    │   │ (Kafka Topic)     │   │  (Kafka Topic)   │
   │                  │   │                   │   │                  │
   │ • task.created   │   │ • task.updated    │   │ • reminder.      │
   │ • task.completed │   │                   │   │   triggered      │
   │ • task.deleted   │   │                   │   │                  │
   └─┬──────┬─────┬──┘   └────────┬──────────┘   └────────┬─────────┘
     │      │     │               │                        │
     │      │     │               │                        │
     ▼      ▼     ▼               ▼                        ▼
   ┌────┐┌─────┐┌──────┐    ┌─────────┐           ┌──────────────┐
   │Aud-││Recu-││Remin-│    │ Audit   │           │  Reminder    │
   │it  ││rren-││der   │    │ Service │           │  Service     │
   │Svc ││ce   ││Supp- │    │ (log)   │           │  (status     │
   │    ││Svc  ││ress  │    │         │           │   update)    │
   └──┬─┘└──┬──┘└──┬───┘    └────┬────┘           └──────┬───────┘
      │     │      │              │                       │
      ▼     ▼      ▼              ▼                       ▼
   ┌─────────────────────────────────────────────────────────────┐
   │                   PostgreSQL (Neon)                          │
   │  ┌──────────┐  ┌───────────┐  ┌────────────┐              │
   │  │ tasks    │  │ reminders │  │ audit_log  │              │
   │  └──────────┘  └───────────┘  └────────────┘              │
   └─────────────────────────────────────────────────────────────┘
```

### 4.2 Task Create → Event → Audit + Reminder Flow

```
User: "Add task: Buy groceries, due tomorrow, daily recurrence"
  │
  ▼
MCP Tool: add_task(title="Buy groceries", due_date="2026-02-10", recurrence="daily")
  │
  ├── 1. DB Write ──────────────────────── tasks table (INSERT)
  │
  ├── 2. Publish Event ─── Dapr Sidecar ──► todo.task-events
  │                                          │
  │                                          ├──► Audit Service
  │                                          │    └── audit_log (INSERT event_id=X)
  │                                          │
  │                                          └──► Recurrence Service
  │                                               └── (no action: not completed)
  │
  └── 3. Response ──► "Task created: Buy groceries"
```

### 4.3 Task Completed → Recurrence → New Task Flow

```
User: "Complete task: Buy groceries"
  │
  ▼
MCP Tool: complete_task(task_id="abc-123")
  │
  ├── 1. DB Write ──────── tasks table (UPDATE completed=true)
  │
  ├── 2. Publish Event ─── Dapr Sidecar ──► todo.task-events (task.completed)
  │                                          │
  │                                          ├──► Audit Service
  │                                          │    └── audit_log (INSERT)
  │                                          │
  │                                          ├──► Recurrence Service
  │                                          │    ├── Check: recurrence="daily" ✓
  │                                          │    ├── Calculate: next_due = 2026-02-11
  │                                          │    ├── DB Write: tasks (INSERT new instance)
  │                                          │    └── Publish: task.created event
  │                                          │
  │                                          └──► Reminder Suppression
  │                                               └── Cancel pending reminders for abc-123
  │
  └── 3. Response ──► "Task completed. Next instance created for 2026-02-11"
```

### 4.4 Reminder Lifecycle Flow

```
User: "Remind me about Buy groceries 30 minutes before"
  │
  ▼
MCP Tool: set_reminder(task_id="abc-123", lead_time="30min")
  │
  ├── 1. Calculate: remind_at = due_date - 30min = 2026-02-10T09:30:00Z
  ├── 2. DB Write ──────── reminders table (INSERT status=PENDING)
  ├── 3. Register Dapr Job (one-time, fires at remind_at)
  └── 4. Response ──► "Reminder set for 2026-02-10 at 9:30 AM"

  ... time passes ...

Dapr Job fires at 2026-02-10T09:30:00Z
  │
  ├── Publish ──► todo.reminders (reminder.triggered)
  │               │
  │               └──► Reminder Service
  │                    ├── Check: task still active? (not completed/deleted)
  │                    ├── If active: status → TRIGGERED, log to audit
  │                    └── If inactive: status → CANCELLED, discard
  │
  └── Done
```

### 4.5 Dead Letter Queue Flow

```
Event published to todo.task-events
  │
  ├── Attempt 1: Consumer fails (e.g., DB connection timeout)
  │   └── Dapr retry: wait 1s
  │
  ├── Attempt 2: Consumer fails
  │   └── Dapr retry: wait 2s (exponential backoff)
  │
  ├── Attempt 3: Consumer fails
  │   └── Dapr retry: wait 4s
  │
  └── Retries exhausted (3 attempts)
      └── Route to ──► todo.task-events.dlq
                       │
                       └── Alert/monitoring picks up DLQ message
                           └── Manual investigation and reprocessing
```

### 4.6 Idempotent Processing Flow

```
Event: task.created (event_id: "evt-001")
  │
  ├── Delivery 1 ──► Audit Service
  │                  ├── Check: SELECT WHERE event_id = "evt-001"
  │                  ├── Not found → INSERT audit_log entry
  │                  └── ACK event ✓
  │
  └── Delivery 2 (duplicate, Dapr at-least-once)
                     ├── Check: SELECT WHERE event_id = "evt-001"
                     ├── Found → Skip (no INSERT)
                     └── ACK event ✓ (no duplicate entry)
```

---

## 5. Deployment Options

### 5.1 Local: Strimzi on Minikube (Primary)

**Architecture**:
```
Minikube Cluster
├── Namespace: kafka
│   ├── Strimzi Kafka Operator (Deployment)
│   ├── todo-kafka (Kafka StatefulSet, 1 broker)
│   └── todo-kafka-zookeeper (ZooKeeper StatefulSet, 1 node)
│
├── Namespace: dapr-system
│   ├── dapr-operator
│   ├── dapr-sidecar-injector
│   ├── dapr-sentry
│   └── dapr-placement
│
└── Namespace: todo-chatbot
    ├── Backend (Deployment + Dapr sidecar)
    ├── Frontend (Deployment + Dapr sidecar)
    ├── Dapr Components (pubsub-kafka, secrets-kubernetes)
    ├── Dapr Subscriptions (task-events, task-updates, reminders)
    └── ConfigMap + Secrets
```

**Resource requirements**: Minikube `--memory 6144 --cpus 4`

**Kafka broker address**: `todo-kafka-kafka-bootstrap.kafka.svc.cluster.local:9092`

### 5.2 Local: Redpanda on Minikube (Alternative)

**Architecture**: Same namespace layout, but Kafka replaced with Redpanda:
```
Namespace: kafka
├── Redpanda Operator (via Helm)
└── redpanda (StatefulSet, 1 broker, no ZooKeeper needed)
```

**Advantages over Strimzi**: Lower memory (~256Mi vs ~768Mi), no ZooKeeper dependency, Kafka-API compatible.

**Kafka broker address**: `redpanda.kafka.svc.cluster.local:9093`

### 5.3 Cloud: Redpanda Cloud (Production)

**Architecture**:
```
Cloud Kubernetes Cluster (AKS / GKE / OKE)
├── Namespace: dapr-system (same as local)
│
└── Namespace: todo-chatbot
    ├── Backend (Deployment + Dapr sidecar, replicas: 2+)
    ├── Frontend (Deployment + Dapr sidecar, replicas: 2+)
    ├── Dapr Components (pubsub-kafka → external Redpanda Cloud)
    ├── Dapr Subscriptions (same as local)
    ├── Ingress / LoadBalancer
    └── ConfigMap + Secrets (including Kafka SASL credentials)

External (Managed):
└── Redpanda Cloud
    ├── todo.task-events (3 partitions, RF=3)
    ├── todo.task-updates (3 partitions, RF=3)
    ├── todo.reminders (1 partition, RF=3)
    └── DLQ topics (auto-created)
```

**Kafka broker address**: `<cluster-id>.redpanda.cloud:9092` (from Redpanda Cloud console)
**Authentication**: SASL/SCRAM (username + password in K8s Secret)

---

## 6. Generated Files Index

| File | Purpose |
|------|---------|
| `helm/todo-chatbot/templates/kafka/strimzi-kafka.yaml` | Strimzi Kafka cluster CRD for local |
| `helm/todo-chatbot/templates/kafka/kafka-topics.yaml` | KafkaTopic CRDs for all 6 topics |
| `helm/todo-chatbot/templates/kafka/redpanda-kafka.yaml` | Alternative Redpanda local deployment |
| `helm/todo-chatbot/templates/dapr-pubsub.yaml` | Dapr Pub/Sub component (Kafka) |
| `helm/todo-chatbot/templates/dapr-subscription.yaml` | Dapr topic subscriptions |
| `helm/todo-chatbot/templates/dapr-resiliency.yaml` | Dapr retry + circuit breaker |
| `helm/todo-chatbot/values-local.yaml` | Minikube overrides (Strimzi broker) |
| `helm/todo-chatbot/values-redpanda-local.yaml` | Minikube overrides (Redpanda broker) |
| `helm/todo-chatbot/values-production.yaml` | Cloud overrides (Redpanda Cloud) |
| `backend/src/events/schemas.py` | Python event envelope models |
