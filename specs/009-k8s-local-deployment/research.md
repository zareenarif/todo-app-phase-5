# Research: Local Kubernetes Deployment

**Feature**: 009-k8s-local-deployment
**Date**: 2026-02-09

## R1: Docker Multi-Stage Build Strategy

**Decision**: Multi-stage builds for both frontend and backend.

**Frontend (Next.js):**
- 3-stage build: deps → builder → runner
- Uses `node:18-alpine` for all stages (matches existing project)
- Requires `output: 'standalone'` in next.config.js
- Final image runs as non-root user `nextjs` (UID 1001)
- Expected image size: ~150MB (vs ~500MB single-stage)

**Backend (FastAPI):**
- 2-stage build: builder → runner
- Uses `python:3.12-slim` (matches existing Dockerfile base)
- Copies only installed packages and source to runner stage
- Final image runs as non-root user `appuser` (UID 1001)
- Expected image size: ~300MB (vs ~800MB with build tools)

**Rationale**: Multi-stage builds satisfy FR-011 (minimize image size)
and constitution Principle VI (non-root containers, pinned tags).

**Alternatives Considered:**
- Single-stage: Larger images, build tools in production (rejected)
- Alpine Python: musl incompatibility with psycopg2-binary (rejected)
- Distroless: Debugging difficulty in local dev context (rejected)

## R2: Minikube Image Loading

**Decision**: `minikube image load <image>` after local Docker build.

**Rationale**: Simplest approach. No registry configuration needed.
Works with any Minikube driver (Docker, Hyperkit, VirtualBox).

**Steps:**
1. Build with Docker Desktop: `docker build -t <name>:<tag> ...`
2. Load into Minikube: `minikube image load <name>:<tag>`
3. In Helm values, set `imagePullPolicy: Never` (local images only)

**Alternatives Considered:**
- `minikube docker-env`: Requires eval in every terminal (rejected)
- Local registry: Extra component to manage (rejected)
- Minikube mount: Only for source, not images (rejected)

## R3: Helm Chart Architecture

**Decision**: Single umbrella chart, no subcharts.

**Chart name**: `todo-chatbot`
**Chart version**: `1.0.0`
**App version**: `1.0.0`

**Template files:**
- `_helpers.tpl` — Common labels, selectors, fullname
- `namespace.yaml` — Namespace creation
- `configmap.yaml` — Non-sensitive config
- `secret.yaml` — References externally created secret
- `frontend-deployment.yaml` — Frontend pods
- `frontend-service.yaml` — Frontend NodePort service
- `backend-deployment.yaml` — Backend pods
- `backend-service.yaml` — Backend ClusterIP service
- `NOTES.txt` — Post-install access instructions

**Rationale**: 2-service application doesn't benefit from subchart
complexity. Shared namespace and config context makes umbrella
chart natural.

## R4: Service Exposure

**Decision**: Frontend = NodePort, Backend = ClusterIP.

**Frontend access flow:**
1. `minikube service todo-chatbot-frontend -n todo-chatbot`
2. Opens browser with auto-assigned NodePort URL
3. Alternatively: `minikube service todo-chatbot-frontend -n todo-chatbot --url`

**Backend access:**
- Internal DNS: `todo-chatbot-backend.todo-chatbot.svc.cluster.local:8000`
- Frontend env: `NEXT_PUBLIC_API_URL=http://todo-chatbot-backend:8000/api/v1`

**Important**: Frontend container needs `NEXT_PUBLIC_API_URL` set at
BUILD TIME for client-side code. For Kubernetes, we set it at runtime
via environment variable. Next.js standalone mode supports runtime
environment injection via `.env.production` or server-side rendering.

**Resolution**: Use server-side API calls or configure
`NEXT_PUBLIC_API_URL` as a build-time argument in the Dockerfile.
For Minikube, the frontend communicates with backend through the
cluster internal DNS since both are in the same cluster.

## R5: Health Check Configuration

**Decision**: HTTP probes for backend, TCP + HTTP for frontend.

**Backend probes:**
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 15
  periodSeconds: 10
  failureThreshold: 3
readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 5
  failureThreshold: 3
```

**Frontend probes:**
```yaml
livenessProbe:
  tcpSocket:
    port: 3000
  initialDelaySeconds: 20
  periodSeconds: 10
  failureThreshold: 3
readinessProbe:
  httpGet:
    path: /
    port: 3000
  initialDelaySeconds: 25
  periodSeconds: 10
  failureThreshold: 3
```

**Rationale**: Backend has a dedicated `/health` endpoint. Frontend
uses TCP for liveness (is the process alive?) and HTTP for readiness
(is it serving pages?).

## R6: Namespace Strategy

**Decision**: `todo-chatbot` namespace, created by Helm chart.

**Rationale**: Isolates from `default` namespace. Allows clean
teardown with `kubectl delete namespace todo-chatbot`.

## R7: Resource Limits

**Decision**: Conservative defaults for Minikube (2 CPU, 4GB RAM).

| Container | CPU Req | CPU Lim | Mem Req | Mem Lim |
|-----------|---------|---------|---------|---------|
| Frontend  | 100m    | 500m    | 128Mi   | 512Mi   |
| Backend   | 200m    | 1000m   | 256Mi   | 1Gi     |

**Total cluster usage**: 300m CPU req, 1.5Gi CPU lim, 384Mi mem req,
1.5Gi mem lim. Well within Minikube defaults.

## R8: AI DevOps Tooling

**Docker AI (Gordon):**
- Used for Dockerfile generation and optimization
- Command: `docker ai "generate a multi-stage Dockerfile for ..."`
- Fallback: Claude Code generates Dockerfiles directly

**kubectl-ai:**
- Used for natural language Kubernetes operations
- Examples: "show me all pods in todo-chatbot namespace",
  "scale backend to 3 replicas", "why is the frontend pod failing?"
- Install: `kubectl krew install ai` or standalone binary

**kagent:**
- Used for cluster health analysis and optimization
- Examples: "analyze resource usage", "check for misconfigurations"
- Install: Follow kagent installation docs

**Note**: These tools are supplementary. All core operations can be
performed with standard kubectl and helm commands.
