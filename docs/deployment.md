# Deployment Guide: Todo AI Chatbot on Kubernetes

**Phase**: 4 — Local Kubernetes Deployment
**Platform**: Minikube (local) with Docker Desktop
**Chart**: `helm/todo-chatbot/` (Helm v3)

---

## Prerequisites

| Tool | Min Version | Install | Verify |
|------|------------|---------|--------|
| Docker Desktop | 4.x | [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/) | `docker --version` |
| Minikube | 1.32+ | [minikube.sigs.k8s.io/docs/start](https://minikube.sigs.k8s.io/docs/start/) | `minikube version` |
| Helm | 3.x | [helm.sh/docs/intro/install](https://helm.sh/docs/intro/install/) | `helm version` |
| kubectl | 1.28+ | Bundled with Docker Desktop / Minikube | `kubectl version --client` |

**System requirements**: 2 CPU cores, 4 GB RAM minimum available for Minikube.

---

## Quick Deploy (5 commands)

```bash
minikube start --cpus=2 --memory=4096
docker build -t todo-backend:1.0.0 -f docker/backend/Dockerfile ./backend && \
docker build -t todo-frontend:1.0.0 -f docker/frontend/Dockerfile ./frontend
minikube image load todo-backend:1.0.0 && minikube image load todo-frontend:1.0.0
kubectl create namespace todo-chatbot && \
kubectl create secret generic todo-secrets --namespace todo-chatbot \
  --from-literal=DATABASE_URL='YOUR_DB_URL' \
  --from-literal=BETTER_AUTH_SECRET='YOUR_SECRET_MIN_32_CHARS' \
  --from-literal=OPENAI_API_KEY='YOUR_KEY' \
  --from-literal=GROQ_API_KEY='YOUR_KEY'
helm install todo-chatbot helm/todo-chatbot/ --namespace todo-chatbot
```

Then access: `minikube service todo-chatbot-frontend -n todo-chatbot`

---

## Step-by-Step Guide

### 1. Start Minikube Cluster

```bash
minikube start --cpus=2 --memory=4096
kubectl cluster-info
```

Expected: Kubernetes control plane running at `https://127.0.0.1:PORT`.

### 2. Build Docker Images

```bash
# Backend (FastAPI + MCP + Agents SDK) — ~2 min
docker build -t todo-backend:1.0.0 -f docker/backend/Dockerfile ./backend

# Frontend (Next.js ChatKit UI) — ~3 min
docker build -t todo-frontend:1.0.0 -f docker/frontend/Dockerfile ./frontend

# Verify
docker images | grep todo-
```

Expected sizes: backend ~300MB, frontend ~150MB.

### 3. Load Images into Minikube

```bash
minikube image load todo-backend:1.0.0
minikube image load todo-frontend:1.0.0

# Verify
minikube image ls | grep todo-
```

### 4. Create Namespace and Secrets

```bash
kubectl create namespace todo-chatbot

kubectl create secret generic todo-secrets \
  --namespace todo-chatbot \
  --from-literal=DATABASE_URL='postgresql://user:pass@host:5432/db' \
  --from-literal=BETTER_AUTH_SECRET='your-secret-key-minimum-32-characters' \
  --from-literal=OPENAI_API_KEY='sk-...' \
  --from-literal=GROQ_API_KEY='gsk_...'
```

### 5. Lint and Deploy

```bash
# Validate chart
helm lint helm/todo-chatbot/

# Dry-run preview
helm install todo-chatbot helm/todo-chatbot/ --namespace todo-chatbot --dry-run

# Deploy
helm install todo-chatbot helm/todo-chatbot/ --namespace todo-chatbot
```

### 6. Verify Deployment

```bash
# Wait for rollout
kubectl rollout status deployment/todo-chatbot-frontend -n todo-chatbot
kubectl rollout status deployment/todo-chatbot-backend -n todo-chatbot

# Check all resources
kubectl get all -n todo-chatbot

# Backend health
kubectl exec -n todo-chatbot deploy/todo-chatbot-backend -- curl -s localhost:8000/health
```

### 7. Access the Application

```bash
# Opens browser automatically
minikube service todo-chatbot-frontend -n todo-chatbot

# Or get URL only
minikube service todo-chatbot-frontend -n todo-chatbot --url
```

---

## Configuration Reference

All configuration is in `helm/todo-chatbot/values.yaml`. Override with `--set` or `-f custom-values.yaml`.

### Replicas

```bash
# Scale backend to 2
helm upgrade todo-chatbot helm/todo-chatbot/ -n todo-chatbot --set backend.replicaCount=2

# Scale frontend to 3
helm upgrade todo-chatbot helm/todo-chatbot/ -n todo-chatbot --set frontend.replicaCount=3
```

### Resources

| Component | CPU Req | CPU Limit | Mem Req | Mem Limit |
|-----------|---------|-----------|---------|-----------|
| Frontend  | 100m    | 500m      | 128Mi   | 512Mi     |
| Backend   | 200m    | 1000m     | 256Mi   | 1Gi       |

```bash
# Increase backend memory
helm upgrade todo-chatbot helm/todo-chatbot/ -n todo-chatbot \
  --set backend.resources.limits.memory=2Gi
```

### Services

| Component | Type | Port | Access |
|-----------|------|------|--------|
| Frontend | NodePort | 3000 | External via `minikube service` |
| Backend | ClusterIP | 8000 | Internal cluster DNS only |

### Health Probes

| Component | Liveness | Readiness |
|-----------|----------|-----------|
| Frontend | TCP :3000 (delay 20s) | HTTP GET / :3000 (delay 25s) |
| Backend | HTTP GET /health :8000 (delay 15s) | HTTP GET /health :8000 (delay 10s) |

### Application Config (ConfigMap)

| Key | Default | Description |
|-----|---------|-------------|
| `config.corsOrigins` | `http://localhost:3000` | CORS allowed origins |
| `config.debug` | `False` | Debug mode |
| `config.llmProvider` | `groq` | LLM provider |
| `config.groqModel` | `llama-3.3-70b-versatile` | Model name |

### Secrets (External)

Created manually before `helm install`:

| Key | Description |
|-----|-------------|
| `DATABASE_URL` | PostgreSQL connection string (Neon) |
| `BETTER_AUTH_SECRET` | Auth secret (min 32 chars) |
| `OPENAI_API_KEY` | OpenAI API key |
| `GROQ_API_KEY` | Groq API key |

---

## Operations

### Upgrade

```bash
# Apply changes from values.yaml
helm upgrade todo-chatbot helm/todo-chatbot/ -n todo-chatbot

# Override specific values
helm upgrade todo-chatbot helm/todo-chatbot/ -n todo-chatbot --set backend.replicaCount=2
```

### Rollback

```bash
# View history
helm history todo-chatbot -n todo-chatbot

# Rollback to revision 1
helm rollback todo-chatbot 1 -n todo-chatbot
```

### View Logs

```bash
# All pods
kubectl logs -n todo-chatbot -l app=todo-chatbot --all-containers

# Backend only
kubectl logs -n todo-chatbot -l component=backend

# Frontend only
kubectl logs -n todo-chatbot -l component=frontend
```

### Resilience Test

```bash
# Delete backend pod — Kubernetes auto-recreates it
kubectl delete pod -n todo-chatbot -l component=backend
kubectl get pods -n todo-chatbot -w
# New pod should reach Running within 60s
```

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `ImagePullBackOff` | Images not loaded in Minikube | `minikube image load todo-backend:1.0.0` |
| `CrashLoopBackOff` | App crash on startup | `kubectl logs -n todo-chatbot <pod>` — check DB URL |
| `Pending` | Insufficient resources | `kubectl describe pod -n todo-chatbot <pod>` — check resources |
| Service not accessible | Minikube tunnel needed | `minikube service todo-chatbot-frontend -n todo-chatbot` |
| DB connection refused | Wrong DATABASE_URL in secret | Recreate secret with correct URL |
| `helm lint` errors | Template syntax issue | Check `helm template helm/todo-chatbot/` output |
| Minikube won't start | Docker not running | Start Docker Desktop first, then `minikube start` |
| 500 error from Docker | Docker service stopped | Run as Admin: `Start-Service com.docker.service` |

---

## Teardown

```bash
helm uninstall todo-chatbot -n todo-chatbot
kubectl delete namespace todo-chatbot
minikube stop
# Optional: full cleanup
minikube delete
```

---

## Architecture

```
                    ┌──────────────────────────────────┐
                    │         Minikube Cluster          │
                    │                                  │
  minikube service  │  ┌───────────┐  ┌────────────┐  │
  ─────────────────▶│  │ Frontend  │─▶│  Backend   │  │
     (NodePort)     │  │ Next.js   │  │  FastAPI   │  │
                    │  │ :3000     │  │  :8000     │  │
                    │  └───────────┘  └─────┬──────┘  │
                    │                       │         │
                    │  ┌──────────┐  ┌──────┴───────┐ │
                    │  │ConfigMap │  │   Secret     │ │
                    │  │CORS, LLM │  │DB, API keys  │ │
                    │  └──────────┘  └──────────────┘ │
                    └──────────────────────────────────┘
                                        │
                                        ▼
                                 Neon PostgreSQL
                                 (external DB)
```

---

*Generated for Phase 4 — Local Kubernetes Deployment | 2026-02-09*
