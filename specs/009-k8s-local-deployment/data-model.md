# Infrastructure Entity Model: Local Kubernetes Deployment

**Feature**: 009-k8s-local-deployment
**Date**: 2026-02-09

## Overview

Phase 4 introduces no new application data models. All application
entities (Task, Conversation, User) are preserved from Phase 3. This
document defines the infrastructure entities that compose the
Kubernetes deployment.

## Infrastructure Entities

### Docker Image: Frontend

| Attribute       | Value                    |
|-----------------|--------------------------|
| Name            | `todo-frontend`          |
| Tag             | `1.0.0`                  |
| Base Image      | `node:18-alpine`         |
| Build Stages    | 3 (deps, builder, runner)|
| Exposed Port    | 3000                     |
| Run User        | `nextjs` (UID 1001)      |
| Build Context   | `./frontend`             |
| Dockerfile Path | `docker/frontend/Dockerfile` |

### Docker Image: Backend

| Attribute       | Value                    |
|-----------------|--------------------------|
| Name            | `todo-backend`           |
| Tag             | `1.0.0`                  |
| Base Image      | `python:3.12-slim`       |
| Build Stages    | 2 (builder, runner)      |
| Exposed Port    | 8000                     |
| Run User        | `appuser` (UID 1001)     |
| Build Context   | `./backend`              |
| Dockerfile Path | `docker/backend/Dockerfile` |

### Helm Chart: todo-chatbot

| Attribute       | Value                    |
|-----------------|--------------------------|
| Chart Name      | `todo-chatbot`           |
| Chart Version   | `1.0.0`                  |
| App Version     | `1.0.0`                  |
| API Version     | `v2`                     |
| Type            | `application`            |
| Path            | `helm/todo-chatbot/`     |

### Kubernetes Namespace

| Attribute       | Value                    |
|-----------------|--------------------------|
| Name            | `todo-chatbot`           |
| Purpose         | Isolate all app resources|
| Created By      | kubectl (pre-install)    |

### Kubernetes Deployment: Frontend

| Attribute       | Value                         |
|-----------------|-------------------------------|
| Name            | `todo-chatbot-frontend`       |
| Replicas        | 1 (configurable)              |
| Image           | `todo-frontend:1.0.0`         |
| Port            | 3000                          |
| Liveness Probe  | TCP :3000                     |
| Readiness Probe | HTTP GET / :3000              |
| CPU Request     | 100m                          |
| CPU Limit       | 500m                          |
| Memory Request  | 128Mi                         |
| Memory Limit    | 512Mi                         |
| Labels          | app=todo-chatbot, component=frontend |

### Kubernetes Deployment: Backend

| Attribute       | Value                         |
|-----------------|-------------------------------|
| Name            | `todo-chatbot-backend`        |
| Replicas        | 1 (configurable)              |
| Image           | `todo-backend:1.0.0`          |
| Port            | 8000                          |
| Liveness Probe  | HTTP GET /health :8000        |
| Readiness Probe | HTTP GET /health :8000        |
| CPU Request     | 200m                          |
| CPU Limit       | 1000m                         |
| Memory Request  | 256Mi                         |
| Memory Limit    | 1Gi                           |
| Labels          | app=todo-chatbot, component=backend |

### Kubernetes Service: Frontend

| Attribute       | Value                         |
|-----------------|-------------------------------|
| Name            | `todo-chatbot-frontend`       |
| Type            | NodePort                      |
| Port            | 3000                          |
| Target Port     | 3000                          |
| Selector        | app=todo-chatbot, component=frontend |

### Kubernetes Service: Backend

| Attribute       | Value                         |
|-----------------|-------------------------------|
| Name            | `todo-chatbot-backend`        |
| Type            | ClusterIP                     |
| Port            | 8000                          |
| Target Port     | 8000                          |
| Selector        | app=todo-chatbot, component=backend |
| Internal DNS    | `todo-chatbot-backend.todo-chatbot.svc.cluster.local` |

### Kubernetes ConfigMap

| Attribute       | Value                         |
|-----------------|-------------------------------|
| Name            | `todo-chatbot-config`         |
| Data Keys       | CORS_ORIGINS, PORT, DEBUG, NEXT_PUBLIC_API_URL |

### Kubernetes Secret

| Attribute       | Value                         |
|-----------------|-------------------------------|
| Name            | `todo-secrets`                |
| Type            | Opaque                        |
| Data Keys       | DATABASE_URL, BETTER_AUTH_SECRET, OPENAI_API_KEY, GROQ_API_KEY |
| Created By      | kubectl (pre-install, manual) |

## Entity Relationships

```
Helm Chart (todo-chatbot)
├── creates → Deployment (frontend)
│   ├── uses → Image (todo-frontend:1.0.0)
│   ├── mounts → ConfigMap (todo-chatbot-config)
│   └── mounts → Secret (todo-secrets)
├── creates → Deployment (backend)
│   ├── uses → Image (todo-backend:1.0.0)
│   ├── mounts → ConfigMap (todo-chatbot-config)
│   ├── mounts → Secret (todo-secrets)
│   └── connects → External DB (Neon PostgreSQL)
├── creates → Service (frontend, NodePort)
│   └── routes to → Deployment (frontend)
├── creates → Service (backend, ClusterIP)
│   └── routes to → Deployment (backend)
└── creates → ConfigMap (todo-chatbot-config)
```
