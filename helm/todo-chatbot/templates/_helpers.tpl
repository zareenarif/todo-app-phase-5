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
