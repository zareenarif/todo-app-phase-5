# Quickstart: Local Kubernetes Deployment

**Feature**: 009-k8s-local-deployment
**Date**: 2026-02-09

## Prerequisites

Ensure the following tools are installed:

| Tool           | Minimum Version | Verify Command         |
|----------------|-----------------|------------------------|
| Docker Desktop | 4.x             | `docker --version`     |
| Minikube       | 1.32+           | `minikube version`     |
| Helm           | 3.x             | `helm version`         |
| kubectl        | 1.28+           | `kubectl version`      |
| kubectl-ai     | latest          | `kubectl ai --version` |
| kagent         | latest          | `kagent --version`     |

**System Requirements**: Minimum 2 CPU cores and 4GB RAM available
for Minikube.

## Step 1: Start Minikube

```bash
minikube start --cpus=2 --memory=4096
kubectl cluster-info
```

## Step 2: Build Docker Images

```bash
# From repository root
docker build -t todo-frontend:1.0.0 -f docker/frontend/Dockerfile ./frontend
docker build -t todo-backend:1.0.0 -f docker/backend/Dockerfile ./backend

# Verify images built
docker images | grep todo-
```

## Step 3: Load Images into Minikube

```bash
minikube image load todo-frontend:1.0.0
minikube image load todo-backend:1.0.0

# Verify images loaded
minikube image ls | grep todo-
```

## Step 4: Create Namespace and Secrets

```bash
# Create namespace
kubectl create namespace todo-chatbot

# Create secrets (replace placeholders with actual values)
kubectl create secret generic todo-secrets \
  --namespace todo-chatbot \
  --from-literal=DATABASE_URL='postgresql://user:pass@host/db' \
  --from-literal=BETTER_AUTH_SECRET='your-32-char-secret-key-here-min' \
  --from-literal=OPENAI_API_KEY='sk-your-openai-key' \
  --from-literal=GROQ_API_KEY='gsk-your-groq-key'
```

## Step 5: Deploy with Helm

```bash
# Lint the chart
helm lint helm/todo-chatbot/

# Dry-run to verify
helm install todo-chatbot helm/todo-chatbot/ \
  --namespace todo-chatbot \
  --dry-run

# Install for real
helm install todo-chatbot helm/todo-chatbot/ \
  --namespace todo-chatbot
```

## Step 6: Verify Deployment

```bash
# Wait for pods to be ready
kubectl rollout status deployment/todo-chatbot-frontend -n todo-chatbot
kubectl rollout status deployment/todo-chatbot-backend -n todo-chatbot

# Check all resources
kubectl get all -n todo-chatbot
```

## Step 7: Access the Application

```bash
# Open frontend in browser
minikube service todo-chatbot-frontend -n todo-chatbot

# Or get URL only
minikube service todo-chatbot-frontend -n todo-chatbot --url
```

## Step 8: Verify Resilience

```bash
# Delete a pod and watch it recover
kubectl delete pod -n todo-chatbot -l component=backend
kubectl get pods -n todo-chatbot -w
```

## Step 9: Upgrade and Rollback

```bash
# Modify values.yaml (e.g., change replicas)
helm upgrade todo-chatbot helm/todo-chatbot/ -n todo-chatbot

# Rollback to previous version
helm rollback todo-chatbot 1 -n todo-chatbot
```

## Step 10: AI DevOps Operations

```bash
# kubectl-ai: Query pod status
kubectl ai "show all pods in todo-chatbot namespace and their status"

# kubectl-ai: Scale deployment
kubectl ai "scale the backend deployment to 2 replicas in todo-chatbot"

# kagent: Cluster analysis
kagent analyze --namespace todo-chatbot
```

## Teardown

```bash
# Remove application
helm uninstall todo-chatbot -n todo-chatbot

# Delete namespace (removes all resources)
kubectl delete namespace todo-chatbot

# Stop Minikube
minikube stop
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Pod stuck in `ImagePullBackOff` | Verify images loaded: `minikube image ls \| grep todo-` |
| Pod stuck in `CrashLoopBackOff` | Check logs: `kubectl logs -n todo-chatbot <pod-name>` |
| Pod stuck in `Pending` | Check resources: `kubectl describe pod -n todo-chatbot <pod-name>` |
| Service not accessible | Verify service: `kubectl get svc -n todo-chatbot` |
| Database connection error | Check secret: `kubectl get secret todo-secrets -n todo-chatbot -o yaml` |
| Minikube won't start | Try: `minikube delete && minikube start --cpus=2 --memory=4096` |
