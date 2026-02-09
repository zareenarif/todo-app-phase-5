# Tasks: Local Kubernetes Deployment

**Input**: Design documents from `/specs/009-k8s-local-deployment/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/helm-values.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths and AI tool used in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project directory structure and prerequisites verification

- [ ] T001 Create docker/ directory structure with docker/frontend/ and docker/backend/ subdirectories
  - **AI Tool**: Claude Code
  - **Input**: plan.md project structure
  - **Command**: `mkdir -p docker/frontend docker/backend`
  - **Expected Output**: Empty directories created at repository root

- [ ] T002 Create helm/todo-chatbot/templates/ directory structure
  - **AI Tool**: Claude Code
  - **Input**: plan.md project structure
  - **Command**: `mkdir -p helm/todo-chatbot/templates`
  - **Expected Output**: Empty Helm chart directory tree created

- [ ] T003 [P] Create docs/ directory for deployment documentation
  - **AI Tool**: Claude Code
  - **Input**: plan.md deliverables
  - **Command**: `mkdir -p docs`
  - **Expected Output**: docs/ directory created (if not existing)

- [ ] T004 Verify prerequisites are installed (Docker, Minikube, Helm, kubectl)
  - **AI Tool**: Claude Code
  - **Input**: quickstart.md prerequisites table
  - **Command**: `docker --version && minikube version && helm version && kubectl version --client`
  - **Expected Output**: Version numbers printed for all four tools

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Application configuration change required before containerization

**CRITICAL**: This phase MUST complete before any user story work begins

- [ ] T005 Update frontend/next.config.js to add output: 'standalone' for production Docker builds
  - **AI Tool**: Claude Code
  - **Input**: research.md R8 decision, frontend/next.config.js (current content)
  - **Action**: Add `output: 'standalone'` to nextConfig object
  - **Expected Output**: `next.config.js` contains `output: 'standalone'` alongside existing `reactStrictMode: true`
  - **Verification**: `cat frontend/next.config.js` shows updated config

- [ ] T006 Start Minikube cluster with required resources
  - **AI Tool**: kubectl / Minikube CLI
  - **Input**: plan.md Step 1
  - **Command**: `minikube start --cpus=2 --memory=4096`
  - **Expected Output**: Minikube cluster running, `kubectl cluster-info` returns cluster details

**Checkpoint**: Foundation ready — user story implementation can now begin

---

## Phase 3: User Story 2 - Containerize Frontend and Backend (Priority: P2) 🎯 MVP Prerequisite

**Goal**: Build production-grade multi-stage Docker images for frontend and backend

**Independent Test**: Build each image and run standalone with `docker run`, verify app starts and responds

**Note**: US2 is implemented before US1 because containers are a prerequisite for Helm deployment

### Implementation for User Story 2

- [ ] T007 [P] [US2] Generate multi-stage Dockerfile for backend in docker/backend/Dockerfile
  - **AI Tool**: Claude Code (or Docker AI Gordon: `docker ai "generate a multi-stage Dockerfile for Python FastAPI app with psycopg2, running as non-root user"`)
  - **Input**: research.md R1 backend strategy, backend/requirements.txt, backend/src/main.py
  - **Action**: Create 2-stage Dockerfile:
    - Stage 1 (`builder`): `python:3.12-slim`, install gcc + libpq-dev, pip install requirements
    - Stage 2 (`runner`): `python:3.12-slim`, create non-root user `appuser` (UID 1001), copy installed packages + source, expose 8000
    - CMD: `sh -c "python -m alembic upgrade head || true; python -m uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}"`
  - **Expected Output**: docker/backend/Dockerfile with 2 stages, pinned base image tag, non-root user
  - **Satisfies**: FR-002, FR-011, FR-012

- [ ] T008 [P] [US2] Generate multi-stage Dockerfile for frontend in docker/frontend/Dockerfile
  - **AI Tool**: Claude Code (or Docker AI Gordon: `docker ai "generate a multi-stage Dockerfile for Next.js 14 standalone app with node:18-alpine"`)
  - **Input**: research.md R1 frontend strategy, frontend/package.json, frontend/next.config.js
  - **Action**: Create 3-stage Dockerfile:
    - Stage 1 (`deps`): `node:18-alpine`, copy package*.json, run `npm ci`
    - Stage 2 (`builder`): `node:18-alpine`, copy deps + source, run `next build`
    - Stage 3 (`runner`): `node:18-alpine`, create non-root user `nextjs` (UID 1001), copy standalone output + public + static, expose 3000
    - CMD: `node server.js`
    - ENV: `HOSTNAME="0.0.0.0"`, `PORT=3000`
  - **Expected Output**: docker/frontend/Dockerfile with 3 stages, pinned base image tag, non-root user
  - **Satisfies**: FR-001, FR-011, FR-012

- [ ] T009 [US2] Build backend Docker image and verify
  - **AI Tool**: Docker CLI
  - **Input**: docker/backend/Dockerfile, backend/ source
  - **Command**: `docker build -t todo-backend:1.0.0 -f docker/backend/Dockerfile ./backend`
  - **Expected Output**: Image builds without errors, `docker images | grep todo-backend` shows image under 1GB
  - **Verification**: `docker run --rm -e DATABASE_URL=sqlite:///./test.db -e BETTER_AUTH_SECRET=test-secret-min-32-chars-long-here -p 8000:8000 todo-backend:1.0.0` starts and responds to `curl http://localhost:8000/health`

- [ ] T010 [US2] Build frontend Docker image and verify
  - **AI Tool**: Docker CLI
  - **Input**: docker/frontend/Dockerfile, frontend/ source
  - **Command**: `docker build -t todo-frontend:1.0.0 -f docker/frontend/Dockerfile ./frontend`
  - **Expected Output**: Image builds without errors, `docker images | grep todo-frontend` shows image under 500MB
  - **Verification**: `docker run --rm -e NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1 -p 3000:3000 todo-frontend:1.0.0` starts and serves UI

- [ ] T011 [US2] Load both Docker images into Minikube
  - **AI Tool**: Minikube CLI
  - **Input**: Built images from T009, T010
  - **Command**: `minikube image load todo-backend:1.0.0 && minikube image load todo-frontend:1.0.0`
  - **Expected Output**: `minikube image ls | grep todo-` shows both images loaded
  - **Depends on**: T009, T010, T006

**Checkpoint**: Both Docker images built, tested standalone, and loaded into Minikube

---

## Phase 4: User Story 1 - Deploy Full System with One Command (Priority: P1) 🎯 MVP

**Goal**: Create Helm chart that deploys the entire system via `helm install`

**Independent Test**: Run `helm install` on clean namespace, verify all pods Running and services accessible

**Depends on**: Phase 3 (US2) — images must be built and loaded into Minikube

### Implementation for User Story 1

- [ ] T012 [P] [US1] Create Helm chart metadata in helm/todo-chatbot/Chart.yaml
  - **AI Tool**: Claude Code
  - **Input**: data-model.md Helm Chart entity
  - **Action**: Create Chart.yaml with apiVersion: v2, name: todo-chatbot, version: 1.0.0, appVersion: 1.0.0, type: application, description
  - **Expected Output**: Valid Chart.yaml file
  - **Satisfies**: FR-003

- [ ] T013 [P] [US1] Create Helm values configuration in helm/todo-chatbot/values.yaml
  - **AI Tool**: Claude Code
  - **Input**: contracts/helm-values.md (complete schema)
  - **Action**: Create values.yaml with all keys from contract: frontend (image, replicas, service, resources, probes), backend (image, replicas, service, resources, probes), config (corsOrigins, debug, ports), secrets (existingSecret name)
  - **Expected Output**: Complete values.yaml matching contract specification
  - **Satisfies**: FR-008

- [ ] T014 [P] [US1] Create Helm template helpers in helm/todo-chatbot/templates/_helpers.tpl
  - **AI Tool**: Claude Code
  - **Input**: data-model.md label requirements (app, component, version)
  - **Action**: Create _helpers.tpl with: `todo-chatbot.name`, `todo-chatbot.fullname`, `todo-chatbot.labels` (app, version, chart), `todo-chatbot.selectorLabels` (app, component)
  - **Expected Output**: Standard Helm helper template with common labels and selectors
  - **Satisfies**: FR-017

- [ ] T015 [P] [US1] Create .helmignore file in helm/todo-chatbot/.helmignore
  - **AI Tool**: Claude Code
  - **Input**: Standard Helm ignore patterns
  - **Action**: Create .helmignore excluding .git, *.swp, *.bak, *.tmp, .DS_Store
  - **Expected Output**: .helmignore with standard exclusions

- [ ] T016 [US1] Create ConfigMap template in helm/todo-chatbot/templates/configmap.yaml
  - **AI Tool**: Claude Code
  - **Input**: data-model.md ConfigMap entity, contracts/helm-values.md config section
  - **Action**: Create ConfigMap template using `{{ .Values.config.* }}` for CORS_ORIGINS, PORT, DEBUG, LLM_PROVIDER, GROQ_MODEL, NEXT_PUBLIC_API_URL (set to backend internal DNS)
  - **Expected Output**: ConfigMap template with values-driven configuration
  - **Satisfies**: FR-006
  - **Depends on**: T014 (_helpers.tpl for labels)

- [ ] T017 [US1] Create Secret reference template in helm/todo-chatbot/templates/secret.yaml
  - **AI Tool**: Claude Code
  - **Input**: data-model.md Secret entity, plan.md Step 4
  - **Action**: Create template that references existing secret `{{ .Values.secrets.existingSecret }}`. This template is a documentation placeholder — actual secret is created manually via kubectl before helm install
  - **Expected Output**: Template file documenting the expected secret structure (or no-op if using external secret)
  - **Satisfies**: FR-005
  - **Depends on**: T014

- [ ] T018 [US1] Create backend Deployment template in helm/todo-chatbot/templates/backend-deployment.yaml
  - **AI Tool**: Claude Code
  - **Input**: data-model.md Backend Deployment entity, contracts/helm-values.md backend section, research.md R5 (health checks), R7 (resources)
  - **Action**: Create Deployment template with:
    - replicas from `{{ .Values.backend.replicaCount }}`
    - image from `{{ .Values.backend.image.repository }}:{{ .Values.backend.image.tag }}`
    - imagePullPolicy: `{{ .Values.backend.image.pullPolicy }}`
    - envFrom: configMapRef (todo-chatbot-config) + secretRef (todo-secrets)
    - livenessProbe: httpGet /health :8000
    - readinessProbe: httpGet /health :8000
    - resources from `{{ .Values.backend.resources }}`
    - labels: app=todo-chatbot, component=backend
  - **Expected Output**: Complete backend Deployment template
  - **Satisfies**: FR-003, FR-007, FR-014
  - **Depends on**: T014, T016, T017

- [ ] T019 [US1] Create backend Service template in helm/todo-chatbot/templates/backend-service.yaml
  - **AI Tool**: Claude Code
  - **Input**: data-model.md Backend Service entity, research.md R4 (ClusterIP)
  - **Action**: Create Service template with type ClusterIP, port 8000, selector component=backend
  - **Expected Output**: Backend ClusterIP Service template
  - **Satisfies**: FR-004, FR-010
  - **Depends on**: T014

- [ ] T020 [US1] Create frontend Deployment template in helm/todo-chatbot/templates/frontend-deployment.yaml
  - **AI Tool**: Claude Code
  - **Input**: data-model.md Frontend Deployment entity, contracts/helm-values.md frontend section, research.md R5 (health checks), R7 (resources)
  - **Action**: Create Deployment template with:
    - replicas from `{{ .Values.frontend.replicaCount }}`
    - image from `{{ .Values.frontend.image.repository }}:{{ .Values.frontend.image.tag }}`
    - imagePullPolicy: `{{ .Values.frontend.image.pullPolicy }}`
    - envFrom: configMapRef + secretRef
    - livenessProbe: tcpSocket :3000
    - readinessProbe: httpGet / :3000
    - resources from `{{ .Values.frontend.resources }}`
    - labels: app=todo-chatbot, component=frontend
  - **Expected Output**: Complete frontend Deployment template
  - **Satisfies**: FR-003, FR-007
  - **Depends on**: T014, T016, T017

- [ ] T021 [US1] Create frontend Service template in helm/todo-chatbot/templates/frontend-service.yaml
  - **AI Tool**: Claude Code
  - **Input**: data-model.md Frontend Service entity, research.md R4 (NodePort)
  - **Action**: Create Service template with type NodePort, port 3000, selector component=frontend
  - **Expected Output**: Frontend NodePort Service template
  - **Satisfies**: FR-004, FR-009
  - **Depends on**: T014

- [ ] T022 [US1] Create NOTES.txt post-install instructions in helm/todo-chatbot/templates/NOTES.txt
  - **AI Tool**: Claude Code
  - **Input**: quickstart.md Step 7 (access instructions)
  - **Action**: Create NOTES.txt with:
    - Instructions to access frontend via `minikube service`
    - Backend health check command
    - Namespace reminder
    - Link to docs/deployment.md
  - **Expected Output**: NOTES.txt displayed after `helm install`
  - **Satisfies**: FR-013

- [ ] T023 [US1] Validate Helm chart with helm lint
  - **AI Tool**: Helm CLI
  - **Input**: Complete helm/todo-chatbot/ chart from T012-T022
  - **Command**: `helm lint helm/todo-chatbot/`
  - **Expected Output**: `0 chart(s) linted, 0 chart(s) failed` (zero errors)
  - **Satisfies**: FR-016
  - **Depends on**: T012-T022

- [ ] T024 [US1] Create Kubernetes namespace and secrets for deployment
  - **AI Tool**: kubectl CLI
  - **Input**: plan.md Step 4, data-model.md Namespace and Secret entities
  - **Command**:
    ```
    kubectl create namespace todo-chatbot
    kubectl create secret generic todo-secrets \
      --namespace todo-chatbot \
      --from-literal=DATABASE_URL='<operator-provides>' \
      --from-literal=BETTER_AUTH_SECRET='<operator-provides>' \
      --from-literal=OPENAI_API_KEY='<operator-provides>' \
      --from-literal=GROQ_API_KEY='<operator-provides>'
    ```
  - **Expected Output**: Namespace and Secret created
  - **Satisfies**: FR-005, FR-015
  - **Depends on**: T006 (Minikube running)

- [ ] T025 [US1] Deploy full system with helm install
  - **AI Tool**: Helm CLI
  - **Input**: Complete Helm chart, loaded images, namespace + secrets
  - **Command**: `helm install todo-chatbot helm/todo-chatbot/ --namespace todo-chatbot`
  - **Expected Output**: Helm release created, all pods reach Running state within 120s
  - **Verification**:
    - `kubectl get pods -n todo-chatbot` — all Running
    - `kubectl get svc -n todo-chatbot` — frontend NodePort, backend ClusterIP
    - `kubectl rollout status deployment/todo-chatbot-frontend -n todo-chatbot`
    - `kubectl rollout status deployment/todo-chatbot-backend -n todo-chatbot`
  - **Satisfies**: SC-001, SC-010
  - **Depends on**: T023, T024, T011

- [ ] T026 [US1] Verify frontend accessibility via Minikube service
  - **AI Tool**: Minikube CLI
  - **Input**: Deployed system from T025
  - **Command**: `minikube service todo-chatbot-frontend -n todo-chatbot --url`
  - **Expected Output**: URL printed, browser opens chatbot UI, UI is interactive
  - **Satisfies**: SC-002

- [ ] T027 [US1] Verify backend health through cluster
  - **AI Tool**: kubectl CLI
  - **Input**: Deployed system from T025
  - **Command**: `kubectl exec -n todo-chatbot deploy/todo-chatbot-backend -- curl -s localhost:8000/health`
  - **Expected Output**: `{"status": "healthy"}`
  - **Satisfies**: SC-010

- [ ] T028 [US1] Verify end-to-end chatbot flow through Kubernetes
  - **AI Tool**: Manual / Browser
  - **Input**: Frontend URL from T026
  - **Action**: Open frontend, send a message, verify AI response is returned
  - **Expected Output**: Message sent through frontend → backend → AI agent → MCP tools → response displayed
  - **Satisfies**: SC-002

**Checkpoint**: Full system deployed via `helm install`, frontend accessible, backend healthy, E2E flow works

---

## Phase 5: User Story 3 - System Resilience and Recovery (Priority: P3)

**Goal**: Verify pods auto-recover after deletion with no data loss

**Independent Test**: Delete pods, verify recreation, confirm data persistence

**Depends on**: Phase 4 (US1) — system must be deployed

### Implementation for User Story 3

- [ ] T029 [US3] Delete backend pod and verify automatic recreation
  - **AI Tool**: kubectl CLI
  - **Input**: Deployed system from T025
  - **Command**: `kubectl delete pod -n todo-chatbot -l component=backend && kubectl get pods -n todo-chatbot -w`
  - **Expected Output**: New backend pod created and reaches Running state within 60 seconds
  - **Satisfies**: SC-003

- [ ] T030 [US3] Delete frontend pod and verify automatic recreation
  - **AI Tool**: kubectl CLI
  - **Input**: Deployed system from T025
  - **Command**: `kubectl delete pod -n todo-chatbot -l component=frontend && kubectl get pods -n todo-chatbot -w`
  - **Expected Output**: New frontend pod created and reaches Running state within 60 seconds
  - **Satisfies**: SC-003

- [ ] T031 [US3] Verify data persistence after pod recreation
  - **AI Tool**: Manual / Browser
  - **Input**: System after pod recreation from T029/T030
  - **Action**: Access chatbot via Minikube service, verify previously created tasks and conversations are still available
  - **Expected Output**: All data intact — external Neon PostgreSQL preserves state across pod restarts
  - **Satisfies**: SC-004

**Checkpoint**: System proven resilient — pods auto-recover, data persists

---

## Phase 6: User Story 4 - Helm Chart Configuration and Management (Priority: P4)

**Goal**: Demonstrate Helm upgrade and rollback with values-driven configuration

**Independent Test**: Modify values.yaml, upgrade, verify changes, rollback, verify restoration

**Depends on**: Phase 4 (US1) — system must be deployed

### Implementation for User Story 4

- [ ] T032 [US4] Perform Helm upgrade with modified replica count
  - **AI Tool**: Helm CLI
  - **Input**: Deployed system, values.yaml
  - **Command**: `helm upgrade todo-chatbot helm/todo-chatbot/ --namespace todo-chatbot --set backend.replicaCount=2`
  - **Expected Output**: `kubectl get pods -n todo-chatbot` shows 2 backend pods Running
  - **Satisfies**: SC-005

- [ ] T033 [US4] Perform Helm upgrade with modified resource limits
  - **AI Tool**: Helm CLI
  - **Input**: Deployed system
  - **Command**: `helm upgrade todo-chatbot helm/todo-chatbot/ --namespace todo-chatbot --set backend.resources.limits.memory=2Gi`
  - **Expected Output**: `kubectl describe pod -n todo-chatbot -l component=backend` shows memory limit of 2Gi
  - **Satisfies**: SC-005

- [ ] T034 [US4] Perform Helm rollback to previous revision
  - **AI Tool**: Helm CLI
  - **Input**: System after upgrades from T032/T033
  - **Command**: `helm rollback todo-chatbot 1 --namespace todo-chatbot`
  - **Expected Output**: System returns to original configuration (1 backend replica, original resource limits), all pods Running
  - **Satisfies**: SC-006

**Checkpoint**: Helm upgrade and rollback demonstrated successfully

---

## Phase 7: User Story 5 - AI DevOps Tooling Demonstration (Priority: P5)

**Goal**: Demonstrate kubectl-ai and kagent for cluster operations

**Independent Test**: Run AI tool commands, verify accurate and useful output

**Depends on**: Phase 4 (US1) — system must be deployed

### Implementation for User Story 5

- [ ] T035 [US5] Use kubectl-ai to query pod status in natural language
  - **AI Tool**: kubectl-ai
  - **Input**: Deployed system
  - **Command**: `kubectl ai "show me all pods in the todo-chatbot namespace and their current status"`
  - **Expected Output**: kubectl-ai returns pod names, status (Running), ready counts, ages
  - **Satisfies**: SC-008

- [ ] T036 [US5] Use kubectl-ai to scale deployment via natural language
  - **AI Tool**: kubectl-ai
  - **Input**: Deployed system
  - **Command**: `kubectl ai "scale the frontend deployment to 2 replicas in todo-chatbot namespace"`
  - **Expected Output**: Frontend scaled to 2 replicas, `kubectl get pods -n todo-chatbot` confirms
  - **Satisfies**: SC-008

- [ ] T037 [US5] Use kubectl-ai to debug a workload
  - **AI Tool**: kubectl-ai
  - **Input**: Deployed system
  - **Command**: `kubectl ai "check if there are any issues with the backend deployment in todo-chatbot namespace"`
  - **Expected Output**: kubectl-ai analyzes deployment and reports status (healthy or identifies issues)
  - **Satisfies**: SC-008

- [ ] T038 [US5] Use kagent for cluster health analysis
  - **AI Tool**: kagent
  - **Input**: Deployed system
  - **Command**: `kagent analyze --namespace todo-chatbot`
  - **Expected Output**: kagent provides health assessment of the todo-chatbot namespace (resource usage, pod health, potential issues)
  - **Satisfies**: SC-008

- [ ] T039 [US5] Reset scaling back to original values
  - **AI Tool**: Helm CLI
  - **Input**: System after scaling from T036
  - **Command**: `helm upgrade todo-chatbot helm/todo-chatbot/ --namespace todo-chatbot -f helm/todo-chatbot/values.yaml`
  - **Expected Output**: System returns to 1 replica each, all pods Running

**Checkpoint**: AI DevOps tooling demonstrated — kubectl-ai and kagent used for query, scale, debug, and analysis

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Documentation and final validation

- [ ] T040 [P] Create deployment documentation in docs/deployment.md
  - **AI Tool**: Claude Code
  - **Input**: quickstart.md, plan.md execution flow, all verification results
  - **Action**: Write comprehensive deployment guide with:
    - Prerequisites (tools and versions)
    - Step-by-step deployment instructions
    - Configuration reference (values.yaml keys)
    - Troubleshooting guide
    - Teardown instructions
  - **Expected Output**: Complete deployment guide at docs/deployment.md
  - **Satisfies**: FR-018

- [ ] T041 [P] Verify all Kubernetes resources have standard labels
  - **AI Tool**: kubectl CLI
  - **Input**: Deployed system
  - **Command**: `kubectl get all -n todo-chatbot --show-labels`
  - **Expected Output**: All resources have app=todo-chatbot, component=(frontend|backend), and version labels
  - **Satisfies**: FR-017

- [ ] T042 Run full end-to-end validation against all success criteria
  - **AI Tool**: Manual / CLI
  - **Input**: Deployed system, SC-001 through SC-010
  - **Action**: Execute each success criterion check:
    - SC-001: helm install completes in <120s ✓
    - SC-002: Frontend accessible, chatbot works ✓
    - SC-003: Pod deletion → auto-recreation <60s ✓
    - SC-004: Data persists across pod restarts ✓
    - SC-005: helm upgrade applies changes ✓
    - SC-006: helm rollback restores previous state ✓
    - SC-007: Docker images build in <5min each ✓
    - SC-008: kubectl-ai and kagent functional ✓
    - SC-009: helm lint passes with 0 errors ✓
    - SC-010: Containers have resource limits and healthy probes ✓
  - **Expected Output**: All 10 success criteria pass

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **US2 Containerize (Phase 3)**: Depends on Foundational — must have standalone config and Minikube running
- **US1 Deploy (Phase 4)**: Depends on US2 — must have Docker images loaded
- **US3 Resilience (Phase 5)**: Depends on US1 — must have system deployed
- **US4 Helm Config (Phase 6)**: Depends on US1 — must have system deployed
- **US5 AI DevOps (Phase 7)**: Depends on US1 — must have system deployed
- **Polish (Phase 8)**: Depends on US1-US5 completion

### User Story Dependencies

- **US2 (P2)**: Foundational only — executes FIRST despite lower priority (prerequisite for US1)
- **US1 (P1)**: Depends on US2 (images required)
- **US3 (P3)**: Depends on US1 (system must be deployed)
- **US4 (P4)**: Depends on US1 (system must be deployed) — can run in parallel with US3
- **US5 (P5)**: Depends on US1 (system must be deployed) — can run in parallel with US3/US4

### Within Each User Story

- Dockerfiles before builds (US2: T007/T008 → T009/T010)
- Helm templates before deployment (US1: T012-T022 → T023 → T025)
- Deployment before verification (US1: T025 → T026-T028)

### Parallel Opportunities

```bash
# Phase 1: All setup tasks can run in parallel
T001, T002, T003 → parallel

# Phase 3 (US2): Dockerfiles can be written in parallel
T007, T008 → parallel (then T009, T010 sequential per image)

# Phase 4 (US1): Chart.yaml, values.yaml, _helpers.tpl, .helmignore in parallel
T012, T013, T014, T015 → parallel
# Then templates (depend on _helpers.tpl) — some parallelizable
T016, T017 → after T014 (can run in parallel with each other)
T018, T019, T020, T021 → after T016, T017 (T19/T21 parallelizable)
T022 → independent of other templates

# Phase 5-7 (US3, US4, US5): Can run in parallel after US1 completes
US3, US4, US5 → parallel after T028
```

---

## Implementation Strategy

### MVP First (US2 + US1)

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: Foundational (T005-T006)
3. Complete Phase 3: US2 Containerize (T007-T011)
4. Complete Phase 4: US1 Deploy (T012-T028)
5. **STOP and VALIDATE**: Full system deployed and accessible
6. If passing → proceed to US3-US5

### Incremental Delivery

1. Setup + Foundational → ready for containerization
2. US2 → Docker images built and tested → MVP building block
3. US1 → Helm deploy works → **MVP COMPLETE**
4. US3 → Resilience verified → production confidence
5. US4 → Helm config management → operational readiness
6. US5 → AI DevOps demonstrated → Phase 4 complete
7. Polish → Documentation and final validation

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- US2 executes before US1 (despite lower priority) because containers are a prerequisite
- US3, US4, US5 can execute in parallel after US1 completes
- Verify each checkpoint before proceeding to next phase
- Commit after each task or logical group
- All infrastructure files are AI-generated (Claude Code primary, Docker AI Gordon and kubectl-ai supplementary)
