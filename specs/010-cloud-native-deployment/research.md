# Research: Cloud-Native Event-Driven Todo AI Chatbot

**Branch**: `010-cloud-native-deployment` | **Date**: 2026-02-09

## R1: Kafka Provider for Local Kubernetes

**Decision**: Strimzi Kafka Operator

**Rationale**: Strimzi is the CNCF-incubating Kafka operator for Kubernetes. It provides CRD-based Kafka cluster management, is well-documented for Minikube, and integrates with Helm for installation. Strimzi manages broker lifecycle, topic creation, and user management declaratively.

**Alternatives considered**:
- **Redpanda (local)**: Kafka-compatible, lower resource footprint, but adds a non-standard component for local development. Better suited for cloud-managed use.
- **Bitnami Kafka Helm chart**: Simpler install but no operator for lifecycle management. Acceptable but less production-aligned.

**Resolution**: Strimzi for local (operator-based, production-like experience). Managed Kafka (Redpanda Cloud or Confluent Cloud) for production.

## R2: Dapr Python SDK Integration with FastAPI

**Decision**: `dapr` Python SDK + `dapr-ext-fastapi` extension

**Rationale**: The official `dapr-ext-fastapi` package provides FastAPI-native integration for Dapr subscriptions (decorator-based route registration) and pub/sub publishing (DaprClient). This avoids raw HTTP calls to the Dapr sidecar and provides type-safe interfaces.

**Alternatives considered**:
- **Raw HTTP to Dapr sidecar**: Functional but verbose, error-prone, and lacks type safety.
- **dapr-ext-grpc**: gRPC-based; adds complexity without benefit for this use case where HTTP is sufficient.

**Resolution**: Use `dapr` + `dapr-ext-fastapi`. Publishing via `DaprClient.publish_event()`, subscribing via `@app.subscribe()` decorator.

## R3: Dapr Jobs API for Scheduled Reminders

**Decision**: Dapr Jobs API (HTTP API)

**Rationale**: Dapr Jobs API provides scheduled job execution without requiring an in-process scheduler. Jobs are registered via the Dapr HTTP API with a schedule or one-time trigger. When the job fires, it invokes a configured endpoint. This eliminates the need for APScheduler or cron within the application, keeping services stateless.

**Alternatives considered**:
- **APScheduler (existing dependency)**: Already in requirements.txt, but runs in-process. Not suitable for Kubernetes (state lost on pod restart, no distribution across replicas).
- **Kubernetes CronJob**: Too coarse-grained (minute-level precision), creates new pods for each execution, not suitable for per-task reminders.
- **External scheduler service**: Over-engineered for this use case.

**Resolution**: Dapr Jobs API. Register one-time jobs with `remind_at` timestamp. Job fires → calls backend endpoint → publishes reminder event.

## R4: Event Envelope Schema

**Decision**: CloudEvents-inspired envelope

**Rationale**: CloudEvents is the CNCF specification for event data. Using a CloudEvents-compatible envelope (`id`, `source`, `type`, `time`, `data`) provides interoperability and is the default format for Dapr Pub/Sub.

**Alternatives considered**:
- **Custom envelope**: Simpler but non-standard; limits future interoperability.
- **Full CloudEvents spec**: Includes optional fields (`datacontenttype`, `dataschema`, `subject`) that add complexity without benefit for this project.

**Resolution**: CloudEvents-compatible subset: `{id, source, type, time, data}`. Dapr natively supports this format.

## R5: Kafka Topic Strategy

**Decision**: Three primary topics + three DLQ topics

**Rationale**: Separating task lifecycle events (`todo.task-events`), reminders (`todo.reminders`), and task updates (`todo.task-updates`) by domain concern allows independent consumer scaling, different retention policies, and clear ownership.

**Topics**:
| Topic | Producer | Consumers | Retention |
|-------|----------|-----------|-----------|
| `todo.task-events` | Backend (on create/complete/delete) | Audit service, Recurrence service | 7 days |
| `todo.task-updates` | Backend (on update) | Audit service | 7 days |
| `todo.reminders` | Dapr Jobs (on reminder fire) | Reminder service | 3 days |
| `todo.task-events.dlq` | Dapr (on retry exhaustion) | Alert/monitoring | 30 days |
| `todo.task-updates.dlq` | Dapr (on retry exhaustion) | Alert/monitoring | 30 days |
| `todo.reminders.dlq` | Dapr (on retry exhaustion) | Alert/monitoring | 30 days |

**Alternatives considered**:
- **Single topic with event type filtering**: Simpler but creates hot topic, limits independent scaling, mixes retention needs.
- **Topic-per-event-type**: Too granular (6+ topics for CRUD); operational overhead without proportional benefit.

**Resolution**: Three domain topics + three DLQ topics. Balanced granularity.

## R6: Container Registry Strategy

**Decision**: GitHub Container Registry (GHCR) as default, cloud-specific registries as alternatives

**Rationale**: GHCR integrates natively with GitHub Actions (same authentication), is free for public repositories, and is cloud-neutral. Cloud-specific registries (ACR, GCR, OCIR) can be used via Helm values overrides for production deployments where the cloud provider's registry offers lower latency or policy compliance.

**Alternatives considered**:
- **Docker Hub**: Rate-limited for free tier; less integrated with GitHub Actions.
- **Cloud-specific only**: Creates provider lock-in in CI/CD pipeline definitions.

**Resolution**: GHCR as default in CI/CD. Cloud registry configurable via values files.

## R7: Strimzi vs Bitnami Kafka for Local

**Decision**: Strimzi Kafka Operator

**Rationale**: Strimzi provides a production-like experience on Minikube via CRDs (`Kafka`, `KafkaTopic`). It manages ZooKeeper (or KRaft), broker configuration, and topic lifecycle declaratively. While heavier than Bitnami, it better prepares for production managed Kafka.

**Resource requirements** (Minikube):
- Strimzi Operator: ~256Mi RAM
- Kafka broker (single node): ~512Mi RAM
- ZooKeeper (single node): ~256Mi RAM
- Total: ~1Gi additional RAM on Minikube

**Minikube recommendation**: Start Minikube with `--memory 6144 --cpus 4` minimum.

**Resolution**: Strimzi. Accept the resource overhead for production fidelity.

## R8: Idempotent Event Processing Strategy

**Decision**: Event ID-based deduplication

**Rationale**: Each event carries a unique `id` field (UUID). Consumers store processed event IDs in the audit log table. Before processing, consumers check if the event ID already exists. If yes, the event is acknowledged without reprocessing.

**Alternatives considered**:
- **Database unique constraints only**: Works for audit log but not for recurrence service (which creates new tasks).
- **Kafka consumer offsets only**: Insufficient for at-least-once delivery with Dapr (which may redeliver).

**Resolution**: Event ID deduplication in consumer logic. Audit log table includes `event_id` with unique constraint. Recurrence service checks for existing task with matching parent reference.

## R9: Cloud Provider Isolation Strategy

**Decision**: Helm values files for provider-specific configuration

**Rationale**: All cloud-specific differences (storage class, load balancer annotations, registry URLs, Kafka broker addresses) are isolated to Helm values files. Chart templates use conditional logic based on values to render provider-appropriate manifests.

**Provider-specific values**:
| Value | AKS | GKE | OKE |
|-------|-----|-----|-----|
| `storageClass` | `managed-premium` | `standard` | `oci-bv` |
| `serviceType` | `LoadBalancer` | `LoadBalancer` | `LoadBalancer` |
| `registry` | `<acr>.azurecr.io` | `gcr.io/<project>` | `<region>.ocir.io/<tenancy>` |
| `kafkaBrokers` | Managed endpoint | Managed endpoint | Managed endpoint |

**Resolution**: Template once, configure per environment via values files.
