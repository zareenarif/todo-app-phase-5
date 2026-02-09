# Feature Specification: Local Kubernetes Deployment

**Feature Branch**: `009-k8s-local-deployment`
**Created**: 2026-02-09
**Status**: Draft
**Input**: User description: "Deploy the Phase III Todo AI Chatbot (Frontend + Backend) on Minikube using Docker containers and Helm charts with AI-assisted DevOps tooling."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Deploy Full System with One Command (Priority: P1)

A DevOps operator wants to deploy the entire Todo AI Chatbot
application (frontend and backend) to a local Kubernetes cluster
using a single Helm install command. The operator runs `helm install`
and the system provisions all necessary containers, services,
configuration, and secrets in the Minikube cluster. After deployment,
both the chatbot frontend and the backend API are accessible and
functional.

**Why this priority**: This is the core deliverable of Phase 4.
Without a working single-command deployment, no other user story
has value. Everything depends on the system being deployable.

**Independent Test**: Can be fully tested by running `helm install`
on a clean Minikube cluster and verifying all pods reach Running
state and services are accessible.

**Acceptance Scenarios**:

1. **Given** a running Minikube cluster with no prior application
   deployment, **When** the operator runs `helm install todo-chatbot
   ./helm/todo-chatbot`, **Then** all pods (frontend and backend)
   reach Running state within 120 seconds.

2. **Given** a successful Helm install, **When** the operator runs
   `minikube service` for the frontend, **Then** the chatbot UI
   opens in a browser and is interactive.

3. **Given** a successful Helm install, **When** the operator sends
   a request to the backend health endpoint through the cluster,
   **Then** the backend responds with a healthy status.

4. **Given** a successful Helm install, **When** the operator
   interacts with the chatbot through the frontend, **Then** the
   message reaches the backend, is processed by the AI agent, and
   a response is returned to the user.

---

### User Story 2 - Containerize Frontend and Backend (Priority: P2)

A DevOps operator wants to build Docker images for both the frontend
and backend applications. The operator uses AI tools (Docker AI
Gordon or Claude Code) to generate optimized Dockerfiles, then builds
the images and loads them into Minikube. Each image runs correctly
as a standalone container.

**Why this priority**: Containers are the prerequisite for Kubernetes
deployment. Without working Docker images, Helm charts cannot deploy
anything. This is the foundational building block.

**Independent Test**: Can be tested by building each Docker image
and running it standalone with `docker run`, verifying the
application starts and responds to requests.

**Acceptance Scenarios**:

1. **Given** the Phase 3 frontend source code, **When** the operator
   builds the frontend Docker image, **Then** the image builds
   successfully without errors and is under 500MB.

2. **Given** the Phase 3 backend source code, **When** the operator
   builds the backend Docker image, **Then** the image builds
   successfully without errors and is under 1GB.

3. **Given** a built frontend image, **When** the operator runs it
   as a standalone container with required environment variables,
   **Then** the frontend application starts and serves the chatbot
   UI on the configured port.

4. **Given** a built backend image, **When** the operator runs it
   as a standalone container with required environment variables,
   **Then** the backend application starts and responds to health
   check requests.

---

### User Story 3 - System Resilience and Recovery (Priority: P3)

A DevOps operator wants to verify that the deployed system survives
pod failures. When a pod is deleted or crashes, Kubernetes
automatically recreates it and the application returns to a fully
functional state without manual intervention or data loss.

**Why this priority**: Resilience validates that the Kubernetes
deployment is production-grade. Pod recovery is a fundamental
Kubernetes capability that must work correctly for the deployment
to be considered successful.

**Independent Test**: Can be tested by deleting pods with `kubectl
delete pod` and verifying they are recreated and reach Running state,
then confirming the application is functional.

**Acceptance Scenarios**:

1. **Given** a fully deployed and functional system, **When** the
   operator deletes the backend pod with `kubectl delete pod`,
   **Then** Kubernetes recreates the pod and it reaches Running
   state within 60 seconds.

2. **Given** a fully deployed and functional system, **When** the
   operator deletes the frontend pod, **Then** the frontend pod
   is recreated and the chatbot UI becomes accessible again within
   60 seconds.

3. **Given** a pod has been deleted and recreated, **When** the
   operator uses the chatbot, **Then** all previously stored data
   (tasks, conversations) is still available because state is
   persisted externally.

---

### User Story 4 - Helm Chart Configuration and Management (Priority: P4)

A DevOps operator wants to customize the deployment by modifying
Helm values (replica count, resource limits, environment variables)
without editing any template files. The operator also wants to
perform upgrades and rollbacks using Helm commands.

**Why this priority**: Configuration management through Helm values
is what makes the deployment reproducible and maintainable. Upgrades
and rollbacks are essential operational capabilities.

**Independent Test**: Can be tested by modifying values.yaml,
running `helm upgrade`, and verifying the changes are applied. Then
running `helm rollback` and verifying the previous state is restored.

**Acceptance Scenarios**:

1. **Given** a deployed system, **When** the operator modifies the
   replica count in values.yaml and runs `helm upgrade`, **Then**
   the number of pods matches the new replica count.

2. **Given** a deployed system, **When** the operator changes
   resource limits in values.yaml and runs `helm upgrade`, **Then**
   the pods are restarted with the new resource limits applied.

3. **Given** a successful upgrade, **When** the operator runs
   `helm rollback`, **Then** the system returns to the previous
   configuration and all pods are functional.

---

### User Story 5 - AI DevOps Tooling Demonstration (Priority: P5)

A DevOps operator wants to use AI-assisted tooling (kubectl-ai,
kagent) to interact with, debug, and optimize the Kubernetes cluster.
The operator issues natural language commands to kubectl-ai for
cluster operations and uses kagent for analysis.

**Why this priority**: AI DevOps tooling is a differentiating feature
of Phase 4 but is supplementary to the core deployment. The system
must work without these tools; they add operational convenience.

**Independent Test**: Can be tested by running kubectl-ai and kagent
commands against the deployed cluster and verifying they produce
correct and useful output.

**Acceptance Scenarios**:

1. **Given** a deployed system, **When** the operator uses
   kubectl-ai to query pod status in natural language, **Then**
   kubectl-ai returns accurate information about pod states.

2. **Given** a deployed system, **When** the operator uses kagent
   to analyze cluster health, **Then** kagent provides a meaningful
   assessment of the deployment.

3. **Given** a deployed system, **When** the operator uses
   kubectl-ai to scale a deployment, **Then** the deployment scales
   to the requested replica count.

---

### Edge Cases

- What happens when Minikube runs out of allocated memory?
  The system MUST fail gracefully with clear error messages indicating
  resource exhaustion. Pod events MUST show OOMKilled or resource
  scheduling failures.

- What happens when the external database (Neon PostgreSQL) is
  unreachable? Backend pods MUST start but readiness probes MUST
  fail, preventing traffic routing. Pod logs MUST indicate the
  database connection failure.

- What happens when Docker images fail to load into Minikube?
  Helm install MUST fail with ImagePullBackOff status on affected
  pods. The error MUST be visible via `kubectl describe pod`.

- What happens when secrets are not configured before deployment?
  Backend pods MUST fail to start with clear environment variable
  errors. The operator MUST be able to diagnose the issue from pod
  logs.

- What happens when the operator runs `helm install` twice with the
  same release name? Helm MUST return an error indicating the
  release already exists, guiding the operator to use `helm upgrade`.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a Dockerfile for the frontend
  application that produces a working container image.

- **FR-002**: System MUST provide a Dockerfile for the backend
  application that produces a working container image.

- **FR-003**: System MUST provide a Helm chart that deploys both
  frontend and backend as separate Kubernetes Deployments.

- **FR-004**: Each Deployment MUST have a corresponding Kubernetes
  Service for network access.

- **FR-005**: System MUST use Kubernetes Secrets to inject sensitive
  configuration (database URL, API keys, auth secrets).

- **FR-006**: System MUST use Kubernetes ConfigMaps for non-sensitive
  configuration (CORS origins, port numbers, backend URL).

- **FR-007**: All containers MUST define health checks (liveness
  and readiness probes) so Kubernetes can monitor application health.

- **FR-008**: The Helm chart MUST allow configuration of replica
  count, resource limits, and environment variables through
  values.yaml without modifying templates.

- **FR-009**: The frontend Service MUST be accessible from outside
  the cluster via Minikube (NodePort or minikube service command).

- **FR-010**: The frontend MUST be able to communicate with the
  backend through Kubernetes internal service DNS.

- **FR-011**: Docker images MUST use multi-stage builds to minimize
  final image size.

- **FR-012**: Docker images MUST use specific base image version
  tags (no `latest` tag).

- **FR-013**: The Helm chart MUST include a NOTES.txt that provides
  post-install instructions for accessing the application.

- **FR-014**: All application logs MUST be written to stdout/stderr
  for access via `kubectl logs`.

- **FR-015**: The system MUST deploy to a dedicated Kubernetes
  namespace.

- **FR-016**: The Helm chart MUST pass `helm lint` validation
  without errors.

- **FR-017**: All Kubernetes resources MUST include standard labels
  (app, component, version).

- **FR-018**: System MUST provide documentation (README) with
  step-by-step deployment instructions.

### Key Entities

- **Docker Image (Frontend)**: A container image packaging the
  Next.js/ChatKit frontend application. Built from a multi-stage
  Dockerfile. Tagged with version for traceability.

- **Docker Image (Backend)**: A container image packaging the
  FastAPI backend with MCP server and OpenAI Agents SDK. Built from
  a multi-stage Dockerfile. Tagged with version for traceability.

- **Helm Chart**: A versioned package containing all Kubernetes
  resource templates (Deployments, Services, ConfigMaps, Secrets)
  and a values.yaml configuration surface. Single umbrella chart
  for the entire application.

- **Kubernetes Namespace**: An isolated environment within the
  Minikube cluster where all application resources are deployed.

- **Kubernetes Secret**: A resource storing sensitive environment
  variables (DATABASE_URL, OPENAI_API_KEY, BETTER_AUTH_SECRET)
  encoded in base64.

- **Kubernetes ConfigMap**: A resource storing non-sensitive
  configuration (CORS_ORIGINS, BACKEND_URL, PORT).

## Assumptions

- Minikube is already installed and operational on the operator's
  machine with sufficient resources (minimum 2 CPU, 4GB RAM).
- Docker Desktop is installed and running.
- The operator has `helm`, `kubectl`, `kubectl-ai`, and `kagent`
  CLI tools installed.
- The Phase 3 application source code (frontend and backend) is
  available and functional.
- The external Neon PostgreSQL database is provisioned and accessible
  from the operator's network.
- Required API keys (OpenAI, Better Auth) are available to the
  operator for secret creation.
- The operator has basic familiarity with terminal commands.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A single `helm install` command deploys the complete
  system (frontend and backend) to a running state within 120
  seconds.

- **SC-002**: The chatbot frontend is accessible via browser through
  Minikube and users can send messages and receive AI responses.

- **SC-003**: Deleting any application pod results in automatic
  recreation with the pod reaching Running state within 60 seconds.

- **SC-004**: All previously stored data (tasks, conversations)
  remains intact after any pod restart or recreation.

- **SC-005**: Modifying values.yaml and running `helm upgrade`
  applies configuration changes without requiring manual
  intervention.

- **SC-006**: Running `helm rollback` restores the previous
  deployment state successfully.

- **SC-007**: Both Docker images build successfully from source in
  under 5 minutes each.

- **SC-008**: AI DevOps tools (kubectl-ai and kagent) can query and
  interact with the deployed cluster successfully.

- **SC-009**: The Helm chart passes `helm lint` with zero errors.

- **SC-010**: All containers start with defined resource limits and
  health checks reporting healthy status.

## Deliverables

- `docker/frontend/Dockerfile` — Multi-stage Dockerfile for frontend
- `docker/backend/Dockerfile` — Multi-stage Dockerfile for backend
- `helm/todo-chatbot/Chart.yaml` — Helm chart metadata
- `helm/todo-chatbot/values.yaml` — Default configuration values
- `helm/todo-chatbot/templates/` — Kubernetes resource templates
- `docs/deployment.md` — Step-by-step deployment instructions
