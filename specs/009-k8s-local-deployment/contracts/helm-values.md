# Helm Values Contract: todo-chatbot

**Feature**: 009-k8s-local-deployment
**Date**: 2026-02-09

## values.yaml Schema

This document defines the complete configuration surface for the
`todo-chatbot` Helm chart. All deployment customization MUST be
done through these values.

### Global

| Key               | Type   | Default        | Description                       |
|-------------------|--------|----------------|-----------------------------------|
| `namespace`       | string | `todo-chatbot` | Kubernetes namespace for all resources |
| `nameOverride`    | string | `""`           | Override chart name               |
| `fullnameOverride`| string | `""`           | Override full release name        |

### Frontend

| Key                              | Type   | Default             | Description                       |
|----------------------------------|--------|---------------------|-----------------------------------|
| `frontend.replicaCount`         | int    | `1`                 | Number of frontend pod replicas   |
| `frontend.image.repository`     | string | `todo-frontend`     | Docker image name                 |
| `frontend.image.tag`            | string | `1.0.0`             | Docker image tag                  |
| `frontend.image.pullPolicy`     | string | `Never`             | Image pull policy (Never for local)|
| `frontend.service.type`         | string | `NodePort`          | Service type                      |
| `frontend.service.port`         | int    | `3000`              | Service port                      |
| `frontend.resources.requests.cpu`    | string | `100m`         | CPU request                       |
| `frontend.resources.requests.memory` | string | `128Mi`        | Memory request                    |
| `frontend.resources.limits.cpu`      | string | `500m`         | CPU limit                         |
| `frontend.resources.limits.memory`   | string | `512Mi`        | Memory limit                      |
| `frontend.livenessProbe.tcpSocket.port` | int | `3000`        | Liveness probe port               |
| `frontend.livenessProbe.initialDelaySeconds` | int | `20`     | Liveness initial delay            |
| `frontend.livenessProbe.periodSeconds`       | int | `10`     | Liveness check period             |
| `frontend.readinessProbe.httpGet.path`       | string | `/`  | Readiness probe path              |
| `frontend.readinessProbe.httpGet.port`       | int | `3000`  | Readiness probe port              |
| `frontend.readinessProbe.initialDelaySeconds`| int | `25`    | Readiness initial delay           |
| `frontend.readinessProbe.periodSeconds`      | int | `10`    | Readiness check period            |

### Backend

| Key                              | Type   | Default             | Description                       |
|----------------------------------|--------|---------------------|-----------------------------------|
| `backend.replicaCount`          | int    | `1`                 | Number of backend pod replicas    |
| `backend.image.repository`      | string | `todo-backend`      | Docker image name                 |
| `backend.image.tag`             | string | `1.0.0`             | Docker image tag                  |
| `backend.image.pullPolicy`      | string | `Never`             | Image pull policy (Never for local)|
| `backend.service.type`          | string | `ClusterIP`         | Service type                      |
| `backend.service.port`          | int    | `8000`              | Service port                      |
| `backend.resources.requests.cpu`     | string | `200m`         | CPU request                       |
| `backend.resources.requests.memory`  | string | `256Mi`        | Memory request                    |
| `backend.resources.limits.cpu`       | string | `1000m`        | CPU limit                         |
| `backend.resources.limits.memory`    | string | `1Gi`          | Memory limit                      |
| `backend.livenessProbe.httpGet.path` | string | `/health`      | Liveness probe path               |
| `backend.livenessProbe.httpGet.port` | int    | `8000`         | Liveness probe port               |
| `backend.livenessProbe.initialDelaySeconds`  | int | `15`     | Liveness initial delay            |
| `backend.livenessProbe.periodSeconds`        | int | `10`     | Liveness check period             |
| `backend.readinessProbe.httpGet.path`        | string | `/health` | Readiness probe path          |
| `backend.readinessProbe.httpGet.port`        | int    | `8000`    | Readiness probe port          |
| `backend.readinessProbe.initialDelaySeconds` | int | `10`     | Readiness initial delay           |
| `backend.readinessProbe.periodSeconds`       | int | `5`      | Readiness check period            |

### Config

| Key                          | Type   | Default                                  | Description                |
|------------------------------|--------|------------------------------------------|----------------------------|
| `config.corsOrigins`         | string | `http://localhost:3000`                  | CORS allowed origins       |
| `config.debug`               | string | `"False"`                                | Debug mode                 |
| `config.backendPort`         | string | `"8000"`                                 | Backend listen port        |
| `config.frontendPort`        | string | `"3000"`                                 | Frontend listen port       |
| `config.llmProvider`         | string | `groq`                                   | LLM provider               |
| `config.groqModel`           | string | `llama-3.3-70b-versatile`                | Groq model name            |

### Secrets

| Key                          | Type   | Default       | Description                     |
|------------------------------|--------|---------------|---------------------------------|
| `secrets.existingSecret`     | string | `todo-secrets`| Name of pre-created K8s Secret  |

**Note**: Secrets are NOT defined in values.yaml. They MUST be
created manually via `kubectl create secret` before Helm install.
The chart references the existing secret by name.

## Override Examples

### Scale frontend to 3 replicas

```bash
helm upgrade todo-chatbot helm/todo-chatbot/ \
  --set frontend.replicaCount=3 \
  -n todo-chatbot
```

### Increase backend memory

```bash
helm upgrade todo-chatbot helm/todo-chatbot/ \
  --set backend.resources.limits.memory=2Gi \
  -n todo-chatbot
```

### Custom values file

```yaml
# custom-values.yaml
frontend:
  replicaCount: 2
backend:
  replicaCount: 2
  resources:
    limits:
      memory: 2Gi
```

```bash
helm upgrade todo-chatbot helm/todo-chatbot/ \
  -f custom-values.yaml \
  -n todo-chatbot
```
