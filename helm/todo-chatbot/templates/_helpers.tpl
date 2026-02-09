{{/*
Common helper templates for todo-chatbot Helm chart.
*/}}

{{/*
Chart name (truncated to 63 chars for K8s label compliance).
*/}}
{{- define "todo-chatbot.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Fully qualified app name (release + chart, truncated to 63 chars).
*/}}
{{- define "todo-chatbot.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Chart label value.
*/}}
{{- define "todo-chatbot.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels applied to ALL resources.
*/}}
{{- define "todo-chatbot.labels" -}}
helm.sh/chart: {{ include "todo-chatbot.chart" . }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app: {{ include "todo-chatbot.name" . }}
version: {{ .Chart.AppVersion | quote }}
{{- end }}

{{/*
Selector labels for frontend.
*/}}
{{- define "todo-chatbot.selectorLabels.frontend" -}}
app: {{ include "todo-chatbot.name" . }}
component: frontend
{{- end }}

{{/*
Selector labels for backend.
*/}}
{{- define "todo-chatbot.selectorLabels.backend" -}}
app: {{ include "todo-chatbot.name" . }}
component: backend
{{- end }}

{{/*
=============================================================================
Dapr Sidecar Annotations
=============================================================================
Injected into pod template metadata.annotations when dapr.enabled=true.
The Dapr sidecar injector reads these annotations to configure the sidecar.

Reference: https://docs.dapr.io/reference/arguments-annotations-overview/
*/}}

{{/*
Dapr annotations for backend pods.
Backend is the primary Dapr citizen: publishes events, subscribes to topics,
uses state store, secrets store, and jobs API.
*/}}
{{- define "todo-chatbot.dapr.annotations.backend" -}}
dapr.io/enabled: "true"
dapr.io/app-id: {{ .Values.dapr.appId | default "todo-backend" | quote }}
dapr.io/app-port: {{ .Values.dapr.appPort | default "8000" | quote }}
dapr.io/app-protocol: "http"
dapr.io/config: {{ include "todo-chatbot.fullname" . }}-dapr-config
dapr.io/enable-api-logging: {{ .Values.dapr.logging.apiLogging | default "true" | quote }}
dapr.io/enable-metrics: {{ .Values.dapr.metrics.enabled | default "true" | quote }}
dapr.io/metrics-port: {{ .Values.dapr.metrics.port | default "9090" | quote }}
dapr.io/log-level: {{ .Values.dapr.logLevel | default "info" | quote }}
dapr.io/sidecar-cpu-request: {{ .Values.dapr.sidecar.resources.requests.cpu | default "100m" | quote }}
dapr.io/sidecar-memory-request: {{ .Values.dapr.sidecar.resources.requests.memory | default "64Mi" | quote }}
dapr.io/sidecar-cpu-limit: {{ .Values.dapr.sidecar.resources.limits.cpu | default "300m" | quote }}
dapr.io/sidecar-memory-limit: {{ .Values.dapr.sidecar.resources.limits.memory | default "256Mi" | quote }}
{{- end }}

{{/*
Dapr annotations for frontend pods.
Frontend uses Dapr only for service invocation (calling backend via Dapr sidecar
instead of direct HTTP). It does NOT publish or subscribe to events.

Service invocation URL pattern:
  http://localhost:3500/v1.0/invoke/todo-backend/method/api/v1/tasks
*/}}
{{- define "todo-chatbot.dapr.annotations.frontend" -}}
dapr.io/enabled: "true"
dapr.io/app-id: {{ .Values.dapr.frontendAppId | default "todo-frontend" | quote }}
dapr.io/app-port: {{ .Values.frontend.service.port | default "3000" | quote }}
dapr.io/app-protocol: "http"
dapr.io/config: {{ include "todo-chatbot.fullname" . }}-dapr-config
dapr.io/enable-api-logging: "false"
dapr.io/enable-metrics: {{ .Values.dapr.metrics.enabled | default "true" | quote }}
dapr.io/log-level: "warn"
dapr.io/sidecar-cpu-request: "50m"
dapr.io/sidecar-memory-request: "32Mi"
dapr.io/sidecar-cpu-limit: "200m"
dapr.io/sidecar-memory-limit: "128Mi"
{{- end }}

{{/*
Kafka broker URL helper.
Resolves the broker address from values, accounting for different providers.
*/}}
{{- define "todo-chatbot.kafka.brokerUrl" -}}
{{- .Values.kafka.brokers | default "localhost:9092" }}
{{- end }}
