# Quickstart: Cloud-Native Event-Driven Todo AI Chatbot

**Branch**: `010-cloud-native-deployment` | **Date**: 2026-02-09

## Prerequisites

### Required Tools

| Tool | Version | Purpose |
|------|---------|---------|
| Docker Desktop | Latest | Container runtime |
| Minikube | v1.32+ | Local Kubernetes cluster |
| kubectl | v1.28+ | Kubernetes CLI |
| Helm | v3.13+ | Package manager |
| Dapr CLI | v1.13+ | Dapr installation and management |
| Git | Latest | Version control |
| Python | 3.12+ | Backend development |
| Node.js | 18+ | Frontend development |

### Required Accounts / Credentials

| Credential | Purpose | Storage |
|------------|---------|---------|
| `DATABASE_URL` | Neon PostgreSQL connection | K8s Secret |
| `OPENAI_API_KEY` | OpenAI API access | K8s Secret |
| `BETTER_AUTH_SECRET` | Auth token signing | K8s Secret |
| `GROQ_API_KEY` | Groq LLM access | K8s Secret |

## Local Deployment (Minikube)

### Step 1: Start Minikube

```bash
minikube start --memory 6144 --cpus 4 --driver=docker
```

### Step 2: Install Dapr on Cluster

```bash
dapr init -k --wait
dapr status -k
```

### Step 3: Install Strimzi Kafka Operator

```bash
helm repo add strimzi https://strimzi.io/charts/
helm install strimzi-kafka-operator strimzi/strimzi-kafka-operator \
  --namespace kafka --create-namespace --wait
```

### Step 4: Deploy Kafka Cluster

```bash
kubectl apply -f helm/todo-chatbot/templates/kafka/ -n todo-chatbot
kubectl wait kafka/todo-kafka --for=condition=Ready --timeout=300s -n todo-chatbot
```

### Step 5: Create Namespace and Secrets

```bash
kubectl create namespace todo-chatbot

kubectl create secret generic todo-secrets \
  --namespace todo-chatbot \
  --from-literal=DATABASE_URL='<your-neon-connection-string>' \
  --from-literal=BETTER_AUTH_SECRET='<your-auth-secret>' \
  --from-literal=OPENAI_API_KEY='<your-openai-key>' \
  --from-literal=GROQ_API_KEY='<your-groq-key>'
```

### Step 6: Build and Load Docker Images

```bash
# Build images
docker build -t todo-backend:1.0.0 -f backend/Dockerfile backend/
docker build -t todo-frontend:1.0.0 -f frontend/Dockerfile frontend/

# Load into Minikube
minikube image load todo-backend:1.0.0
minikube image load todo-frontend:1.0.0
```

### Step 7: Deploy with Helm

```bash
helm install todo-chatbot helm/todo-chatbot/ \
  -f helm/todo-chatbot/values-local.yaml \
  --namespace todo-chatbot \
  --wait --timeout 5m
```

### Step 8: Verify Deployment

```bash
# Check all pods are Running
kubectl get pods -n todo-chatbot

# Check Dapr sidecars
dapr status -k

# Check Kafka topics
kubectl exec -it todo-kafka-0 -n todo-chatbot -- \
  bin/kafka-topics.sh --list --bootstrap-server localhost:9092

# Access frontend
minikube service frontend -n todo-chatbot
```

## Cloud Deployment

### Step 1: Configure kubectl for Cloud Cluster

```bash
# AKS example:
az aks get-credentials --resource-group <rg> --name <cluster>

# GKE example:
gcloud container clusters get-credentials <cluster> --zone <zone>

# OKE example:
oci ce cluster create-kubeconfig --cluster-id <ocid>
```

### Step 2: Install Dapr on Cloud Cluster

```bash
dapr init -k --wait
```

### Step 3: Configure Managed Kafka

Update `values-production.yaml` with your managed Kafka broker addresses.

### Step 4: Create Secrets

```bash
kubectl create namespace todo-chatbot

kubectl create secret generic todo-secrets \
  --namespace todo-chatbot \
  --from-literal=DATABASE_URL='<production-db-url>' \
  --from-literal=BETTER_AUTH_SECRET='<production-auth-secret>' \
  --from-literal=OPENAI_API_KEY='<production-openai-key>' \
  --from-literal=GROQ_API_KEY='<production-groq-key>'
```

### Step 5: Deploy with Helm

```bash
helm install todo-chatbot helm/todo-chatbot/ \
  -f helm/todo-chatbot/values-production.yaml \
  --namespace todo-chatbot \
  --wait --timeout 5m
```

## Validation Checklist

- [ ] All pods in `Running` state
- [ ] Dapr sidecars injected (check annotations)
- [ ] Kafka broker accessible
- [ ] Kafka topics created (todo.task-events, todo.reminders, todo.task-updates)
- [ ] Frontend accessible via browser
- [ ] Backend health check returns 200 (`/health`)
- [ ] Create a task → verify event on `todo.task-events` topic
- [ ] Complete a recurring task → verify new task instance created
- [ ] Set a reminder → verify it fires at scheduled time
- [ ] Query audit log → verify entries exist
- [ ] Kill a pod → verify recovery without data loss
- [ ] `helm upgrade` → verify rolling update with zero downtime

## Troubleshooting

| Issue | Check | Fix |
|-------|-------|-----|
| Pods stuck in Pending | `kubectl describe pod <name>` | Increase Minikube resources |
| Dapr sidecar not injected | Check pod annotations | Add `dapr.io/enabled: "true"` annotation |
| Kafka connection refused | `kubectl logs <kafka-pod>` | Wait for Kafka StatefulSet to be Ready |
| Events not flowing | `dapr dashboard -k` | Verify Dapr Pub/Sub component config |
| Image pull errors (cloud) | Check registry credentials | Create imagePullSecret |

## Rollback

```bash
# View release history
helm history todo-chatbot -n todo-chatbot

# Rollback to previous version
helm rollback todo-chatbot <revision> -n todo-chatbot

# Verify rollback
kubectl rollout status deployment/backend -n todo-chatbot
kubectl rollout status deployment/frontend -n todo-chatbot
```
