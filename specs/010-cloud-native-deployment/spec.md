# Feature Specification: Cloud-Native Event-Driven Todo AI Chatbot

**Feature Branch**: `010-cloud-native-deployment`
**Created**: 2026-02-09
**Status**: Draft
**Input**: User description: "Phase V Advanced Cloud Deployment — event-driven architecture with Kafka, Dapr, CI/CD, and multi-cloud Kubernetes"

## Assumptions

- The existing Task model already supports `priority` (HIGH/MEDIUM/LOW), `due_date`, `recurrence` (DAILY/WEEKLY/MONTHLY), and `tags` (JSON array) fields from Phase 3. Phase 5 extends these with full event-driven behavior (publishing events on mutations, asynchronous reminders, recurring task generation).
- The existing MCP tools (add_task, list_tasks, complete_task, delete_task, update_task) are preserved and extended to publish events via Dapr Pub/Sub after each operation.
- Better Auth authentication is preserved unchanged. User isolation (`user_id`) continues to apply to all new entities.
- The existing Helm chart structure (helm/todo-chatbot/) is extended, not replaced.
- Kafka topic naming follows the convention `todo.<domain>.<event-type>`.
- Dapr Jobs API is used for scheduled reminder delivery. Reminders trigger at the configured time and publish a notification event.
- Audit log is an append-only record of all task mutations, maintained by a Kafka consumer.
- "Real-time updates" means the backend publishes events that can be consumed by interested services; frontend polling or WebSocket integration is out of scope for Phase 5 unless explicitly added later.
- Local Kafka provider is Strimzi (Kubernetes-native operator) for Minikube; cloud Kafka provider is Redpanda Cloud or Confluent Cloud (configurable via Helm values).
- Search, filter, and sort capabilities apply to the existing task list endpoint, extended with query parameters.
- Reminder notifications are logged and stored; push notification delivery (email, SMS, push) is out of scope for Phase 5.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Event-Driven Task Operations (Priority: P1)

As a user, I want all my task operations (create, update, complete, delete) to publish events so that other system components (audit log, recurring task generator, reminder scheduler) can react asynchronously without blocking my workflow.

**Why this priority**: This is the foundational event-driven capability. Without event publishing, no downstream consumer (audit, reminders, recurrence) can function. Every other user story depends on this infrastructure being in place.

**Independent Test**: Can be fully tested by creating, updating, completing, and deleting a task via the chatbot and verifying that corresponding events appear on the Kafka topic. Delivers event-driven decoupling as immediate value.

**Acceptance Scenarios**:

1. **Given** a user creates a task via the chatbot, **When** the task is persisted in the database, **Then** a `task.created` event is published to the `todo.task-events` topic containing the full task payload and user ID.
2. **Given** a user updates a task, **When** the update is persisted, **Then** a `task.updated` event is published with the before and after state.
3. **Given** a user completes a task, **When** the task is marked completed, **Then** a `task.completed` event is published.
4. **Given** a user deletes a task, **When** the task is removed, **Then** a `task.deleted` event is published with the task ID and user ID.
5. **Given** the Kafka broker is temporarily unavailable, **When** a task operation is performed, **Then** the operation succeeds (database write is not blocked) and the event is retried via Dapr resiliency policy.

---

### User Story 2 - Task Search, Filter, and Sort (Priority: P2)

As a user, I want to search my tasks by keyword, filter them by priority/status/tags/due date, and sort results by various criteria so that I can quickly find the tasks I need.

**Why this priority**: Search, filter, and sort are core usability features that make the task list practical for users with many tasks. They build on existing data without requiring new entities.

**Independent Test**: Can be tested by creating several tasks with different priorities, tags, and due dates, then searching/filtering/sorting via the chatbot and verifying correct results.

**Acceptance Scenarios**:

1. **Given** a user has multiple tasks, **When** they search for "meeting", **Then** only tasks containing "meeting" in the title or description are returned.
2. **Given** a user has tasks with different priorities, **When** they filter by "HIGH" priority, **Then** only high-priority tasks are returned.
3. **Given** a user has tasks with various tags, **When** they filter by tag "work", **Then** only tasks tagged "work" are returned.
4. **Given** a user has tasks with due dates, **When** they filter for tasks due this week, **Then** only tasks with due dates within the current week are returned.
5. **Given** a user requests sorted results, **When** they sort by due date ascending, **Then** tasks are returned in chronological order by due date.
6. **Given** a user combines filters, **When** they filter by priority "HIGH" AND tag "work" sorted by due date, **Then** only matching tasks are returned in the correct order.

---

### User Story 3 - Reminders (Priority: P3)

As a user, I want to set reminders on my tasks so that I receive a notification before a task is due, helping me stay on track without manually checking deadlines.

**Why this priority**: Reminders add proactive value by alerting users to approaching deadlines. They depend on the event-driven infrastructure (US1) and the due date field.

**Independent Test**: Can be tested by creating a task with a due date and reminder, advancing time (or using a short reminder window), and verifying the reminder event is published and logged.

**Acceptance Scenarios**:

1. **Given** a user creates a task with a due date, **When** they set a reminder for 30 minutes before the due date, **Then** the reminder is scheduled and stored.
2. **Given** a reminder is scheduled, **When** the reminder time arrives, **Then** a `reminder.triggered` event is published to the `todo.reminders` topic.
3. **Given** a reminder event is published, **When** the reminder consumer processes it, **Then** the reminder is logged in the audit trail with the task details and user ID.
4. **Given** a task is completed before the reminder fires, **When** the reminder time arrives, **Then** the reminder is suppressed (not delivered).
5. **Given** a task is deleted, **When** the associated reminder exists, **Then** the reminder is cancelled.

---

### User Story 4 - Recurring Tasks (Priority: P4)

As a user, I want to mark tasks as recurring (daily, weekly, monthly) so that the system automatically generates the next instance when I complete the current one, saving me from manual re-creation.

**Why this priority**: Recurring tasks build on the event-driven infrastructure (US1) and existing recurrence field. They require a consumer that listens for `task.completed` events and generates new task instances.

**Independent Test**: Can be tested by creating a recurring task, completing it, and verifying that a new task instance is automatically created with the next due date.

**Acceptance Scenarios**:

1. **Given** a user creates a task with recurrence set to "DAILY" and a due date of today, **When** the user completes the task, **Then** a new task is automatically created with the same title, description, priority, and tags, with the due date set to tomorrow.
2. **Given** a task has recurrence "WEEKLY", **When** it is completed, **Then** the next instance due date is 7 days after the original due date.
3. **Given** a task has recurrence "MONTHLY", **When** it is completed, **Then** the next instance due date is one calendar month after the original due date.
4. **Given** a recurring task is deleted (not completed), **When** the deletion event fires, **Then** no new instance is generated.
5. **Given** the recurring task generator creates a new task, **When** the new task is persisted, **Then** a `task.created` event is published for the new instance.

---

### User Story 5 - Audit Log via Event Consumers (Priority: P5)

As a system administrator, I want an append-only audit log of all task operations so that I can track the history of changes for compliance and debugging purposes.

**Why this priority**: The audit log is a pure consumer of events from US1. It provides operational visibility and compliance value without affecting the user-facing workflow.

**Independent Test**: Can be tested by performing various task operations and querying the audit log to verify all events are recorded with correct timestamps, user IDs, and event types.

**Acceptance Scenarios**:

1. **Given** any task operation occurs (create, update, complete, delete), **When** the event is published, **Then** the audit log consumer persists a record with: event ID, event type, user ID, task ID, timestamp, and payload.
2. **Given** the audit log contains records, **When** an administrator queries by user ID, **Then** all task operations for that user are returned in chronological order.
3. **Given** the audit log consumer fails to process an event, **When** the event is retried, **Then** the audit log entry is created without duplicates (idempotent processing).
4. **Given** a dead letter event occurs, **When** the event cannot be processed after retries, **Then** the event is routed to the dead letter topic and an alert is logged.

---

### User Story 6 - Local Kubernetes Deployment with Dapr and Kafka (Priority: P6)

As a developer, I want to deploy the entire system (application, Kafka, Dapr) on a local Minikube cluster using Helm so that I can develop and test the event-driven architecture locally before deploying to the cloud.

**Why this priority**: Local deployment is the prerequisite for development and testing of all features. It must work reliably before cloud deployment is attempted.

**Independent Test**: Can be tested by running `helm install` on a Minikube cluster with Dapr and Kafka installed, verifying all pods reach Running state, and performing an end-to-end task operation with event verification.

**Acceptance Scenarios**:

1. **Given** a clean Minikube cluster with Dapr installed, **When** `helm install` is run with local values, **Then** all pods (frontend, backend, Kafka) reach Running state within 5 minutes.
2. **Given** the system is deployed locally, **When** a user creates a task via the frontend, **Then** the task is persisted and a `task.created` event appears on the Kafka topic.
3. **Given** Dapr sidecars are injected, **When** the backend publishes via the Dapr Pub/Sub API, **Then** the event is delivered to Kafka without the application using a Kafka client SDK.
4. **Given** a pod is killed, **When** Kubernetes restarts it, **Then** the system recovers without data loss and event processing resumes.
5. **Given** `helm upgrade` is run with updated values, **Then** a rolling update occurs with zero downtime.

---

### User Story 7 - Cloud Kubernetes Deployment (Priority: P7)

As a DevOps engineer, I want to deploy the system to a production cloud Kubernetes cluster (AKS, GKE, or OKE) using the same Helm charts with environment-specific overrides so that the application runs in production with managed infrastructure.

**Why this priority**: Cloud deployment is the ultimate deliverable of Phase 5 but depends on all preceding stories being functional locally first.

**Independent Test**: Can be tested by running `helm install` against a cloud Kubernetes cluster with the production values file and verifying all pods run, events flow, and the application is accessible via a public endpoint.

**Acceptance Scenarios**:

1. **Given** a cloud Kubernetes cluster with Dapr installed, **When** `helm install` is run with production values, **Then** all pods reach Running state.
2. **Given** the production deployment uses a managed Kafka service (Redpanda Cloud or Confluent Cloud), **When** the Dapr Pub/Sub component is configured with the managed broker address, **Then** events flow correctly between services.
3. **Given** the cloud deployment, **When** a user accesses the frontend via the cloud load balancer or ingress, **Then** the full application flow works end-to-end.
4. **Given** environment-specific values (production), **When** compared to local values, **Then** the only differences are: broker addresses, registry URLs, resource limits, replica counts, and service types (LoadBalancer vs NodePort).
5. **Given** the same Helm chart is used for both local and cloud, **When** deploying to a different cloud provider, **Then** only the values file changes — no chart template modifications are needed.

---

### User Story 8 - CI/CD Pipeline (Priority: P8)

As a DevOps engineer, I want an automated CI/CD pipeline via GitHub Actions that builds, tests, pushes container images, and deploys to the target Kubernetes environment so that every merge to main results in a verified, automated deployment.

**Why this priority**: CI/CD automation is the final operational piece. It depends on the Helm charts and deployment stories (US6, US7) being validated manually first.

**Independent Test**: Can be tested by pushing a commit to the main branch and verifying the GitHub Actions workflow runs successfully: lint, test, build, push images, and deploy via Helm.

**Acceptance Scenarios**:

1. **Given** a push or pull request to the main branch, **When** the CI workflow triggers, **Then** it lints the codebase, runs tests, builds Docker images, and pushes them to the container registry.
2. **Given** the CI workflow passes, **When** the CD workflow triggers, **Then** it deploys to the target Kubernetes environment via `helm upgrade --install`.
3. **Given** the pipeline uses GitHub Actions secrets, **When** the workflow runs, **Then** no secrets are exposed in logs or artifacts.
4. **Given** a deployment fails, **When** the CD workflow detects the failure, **Then** it rolls back to the previous Helm release.
5. **Given** Docker images are built, **When** they are pushed to the registry, **Then** they are tagged with both the commit SHA and the semantic version.

---

### Edge Cases

- What happens when Kafka is unavailable during a task operation? The database write succeeds; the event publish is retried via Dapr resiliency policy. If retries are exhausted, the event is routed to a dead letter topic.
- What happens when a recurring task has no due date? Recurrence without a due date is rejected at creation time with a validation error ("Recurring tasks MUST have a due date").
- What happens when a reminder is set for a time that has already passed? The reminder fires immediately upon scheduling.
- What happens when duplicate events are delivered? All consumers MUST be idempotent — duplicate processing produces the same result as single processing.
- What happens when the audit log consumer is down? Events accumulate in Kafka (retention policy ensures they are not lost). When the consumer recovers, it processes the backlog.
- What happens when a search query returns no results? An empty result set is returned with a count of zero; no error is raised.
- What happens when Dapr sidecar is not injected? The pod MUST fail readiness checks and not receive traffic until the sidecar is healthy.
- What happens when a Helm upgrade fails mid-rollout? Kubernetes rolling update strategy ensures the previous version remains active until new pods pass health checks. `helm rollback` restores the last known good state.

## Requirements *(mandatory)*

### Functional Requirements

**Task Features (Extending Existing):**
- **FR-001**: System MUST publish a domain event to Kafka (via Dapr Pub/Sub) for every task mutation (create, update, complete, delete).
- **FR-002**: System MUST support searching tasks by keyword across title and description fields.
- **FR-003**: System MUST support filtering tasks by priority (HIGH, MEDIUM, LOW), completion status, tags, and due date range.
- **FR-004**: System MUST support sorting tasks by due date, priority, creation date, or title in ascending or descending order.
- **FR-005**: System MUST allow combining multiple filters and sort criteria in a single query.

**Reminders:**
- **FR-006**: System MUST allow users to set a reminder on any task that has a due date.
- **FR-007**: System MUST support reminder lead times (e.g., 15 minutes, 30 minutes, 1 hour, 1 day before due date).
- **FR-008**: System MUST deliver reminders asynchronously via the `todo.reminders` Kafka topic at the scheduled time using Dapr Jobs API.
- **FR-009**: System MUST suppress reminders for tasks that are completed or deleted before the reminder fires.
- **FR-010**: System MUST allow users to cancel or update reminders.

**Recurring Tasks:**
- **FR-011**: System MUST automatically generate the next task instance when a recurring task is completed.
- **FR-012**: System MUST calculate the next due date based on the recurrence pattern (DAILY: +1 day, WEEKLY: +7 days, MONTHLY: +1 calendar month).
- **FR-013**: System MUST preserve title, description, priority, tags, and recurrence pattern in the generated instance.
- **FR-014**: System MUST NOT generate a new instance when a recurring task is deleted.

**Audit Log:**
- **FR-015**: System MUST maintain an append-only audit log of all task operations via a Kafka consumer.
- **FR-016**: Each audit log entry MUST contain: event ID, event type, user ID, task ID, timestamp, and event payload.
- **FR-017**: Audit log processing MUST be idempotent (duplicate events produce no duplicate entries).

**Event-Driven Infrastructure:**
- **FR-018**: All Kafka interaction MUST be abstracted via Dapr Pub/Sub — application code MUST NOT use a Kafka client SDK directly.
- **FR-019**: System MUST define dead letter topics for all subscriptions to handle unprocessable events.
- **FR-020**: Events MUST follow a consistent envelope: `{id, source, type, timestamp, data}`.
- **FR-021**: Event consumers MUST be idempotent.

**Deployment:**
- **FR-022**: System MUST deploy to local Minikube via Helm with Dapr and Kafka running in-cluster.
- **FR-023**: System MUST deploy to production cloud Kubernetes (AKS, GKE, or OKE) via the same Helm charts with environment-specific values.
- **FR-024**: System MUST include a CI pipeline (GitHub Actions) that lints, tests, builds Docker images, and pushes to a container registry.
- **FR-025**: System MUST include a CD pipeline (GitHub Actions) that deploys to the target environment via Helm.
- **FR-026**: All secrets MUST be managed via Kubernetes Secrets and GitHub Actions secrets — never hardcoded.

**Observability:**
- **FR-027**: All application logs MUST be written to stdout/stderr for kubectl access.
- **FR-028**: Backend MUST expose health check endpoints (/health, /ready).
- **FR-029**: Kafka consumer lag MUST be observable via metrics or CLI tooling.
- **FR-030**: Dapr sidecar health MUST be included in pod readiness checks.

**MCP Tool Extensions:**
- **FR-031**: Existing MCP tools MUST be extended to support search, filter, and sort parameters.
- **FR-032**: New MCP tools MUST be added for reminder management (set_reminder, cancel_reminder, list_reminders).
- **FR-033**: MCP tools MUST remain stateless and publish events after successful database operations.

### Key Entities

- **Task**: Existing entity (id, user_id, title, description, completed, priority, tags, due_date, recurrence, created_at, updated_at). No schema changes required.
- **Reminder**: New entity representing a scheduled reminder (id, user_id, task_id, remind_at, status [PENDING/TRIGGERED/CANCELLED], created_at). Associated with a Task via task_id. Associated with a User via user_id.
- **AuditLogEntry**: New entity representing an append-only audit record (id, event_id, event_type, user_id, task_id, timestamp, payload). Not editable or deletable by users.
- **TaskEvent**: Logical entity representing the event envelope published to Kafka (id, source, type, timestamp, data). Not persisted in the application database — exists only on Kafka topics.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All task operations (create, update, complete, delete) result in a corresponding event being published within 2 seconds of the database write.
- **SC-002**: Users can search across 1,000+ tasks and receive results within 3 seconds.
- **SC-003**: Reminders fire within 60 seconds of their scheduled time.
- **SC-004**: Recurring task generation creates the next instance within 5 seconds of the current instance being completed.
- **SC-005**: The audit log captures 100% of task operations with zero data loss under normal operating conditions.
- **SC-006**: Local Minikube deployment completes (all pods Running) within 5 minutes of `helm install`.
- **SC-007**: Cloud deployment uses the identical Helm chart as local — only values files differ.
- **SC-008**: CI pipeline completes (lint, test, build, push) within 10 minutes.
- **SC-009**: System survives pod restarts with zero data loss — all state persisted in external database, events retained in Kafka.
- **SC-010**: The same application code runs on Minikube, AKS, GKE, and OKE without modification — cloud neutrality is verified by Helm chart portability.
