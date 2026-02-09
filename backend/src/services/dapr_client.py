"""
Dapr Client — Unified HTTP client for all Dapr building block APIs.

Provides typed methods for:
  - State Store:       GET/POST/DELETE state
  - Secrets Store:     GET secrets
  - Jobs API:          Schedule and manage one-time/recurring jobs
  - Service Invocation: Call other Dapr apps via sidecar proxy
  - Health Check:      Verify Dapr sidecar is healthy

All methods use the Dapr sidecar HTTP API (localhost:3500).
No Kafka, PostgreSQL, or Kubernetes SDK required in application code.

Reference: https://docs.dapr.io/reference/api/
"""

from __future__ import annotations

import logging
import os
from typing import Any, Optional

import httpx

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Dapr sidecar configuration
# ---------------------------------------------------------------------------
DAPR_HTTP_PORT = int(os.getenv("DAPR_HTTP_PORT", "3500"))
DAPR_BASE_URL = f"http://localhost:{DAPR_HTTP_PORT}"


class DaprClient:
    """
    Typed HTTP client for the Dapr sidecar API.

    Usage:
        client = DaprClient()

        # State store
        await client.save_state("statestore-postgres", "key1", {"foo": "bar"})
        value = await client.get_state("statestore-postgres", "key1")

        # Secrets
        secret = await client.get_secret("secrets-kubernetes", "todo-secrets", "DATABASE_URL")

        # Service invocation
        resp = await client.invoke_service("todo-backend", "api/v1/tasks", method="GET")

        # Jobs API (reminder scheduling)
        await client.schedule_job("reminder-abc", schedule=None, due_time="2026-02-10T09:30:00Z",
                                  data={"reminder_id": "abc"})
    """

    def __init__(self, base_url: str = DAPR_BASE_URL) -> None:
        self._base_url = base_url
        self._client = httpx.AsyncClient(base_url=base_url, timeout=10.0)

    # =====================================================================
    # STATE STORE — key/value storage via Dapr
    # API: /v1.0/state/{storename}
    # =====================================================================

    async def save_state(
        self, store_name: str, key: str, value: Any, metadata: Optional[dict] = None
    ) -> bool:
        """
        Save a key/value pair to a Dapr state store.

        URL: POST /v1.0/state/{storename}
        """
        payload = [{"key": key, "value": value}]
        if metadata:
            payload[0]["metadata"] = metadata
        try:
            resp = await self._client.post(f"/v1.0/state/{store_name}", json=payload)
            return resp.status_code in (200, 204)
        except httpx.HTTPError as exc:
            logger.error("State save failed: store=%s key=%s error=%s", store_name, key, exc)
            return False

    async def get_state(self, store_name: str, key: str) -> Optional[Any]:
        """
        Retrieve a value from a Dapr state store.

        URL: GET /v1.0/state/{storename}/{key}
        Returns None if key does not exist.
        """
        try:
            resp = await self._client.get(f"/v1.0/state/{store_name}/{key}")
            if resp.status_code == 200 and resp.text:
                return resp.json()
            return None
        except httpx.HTTPError as exc:
            logger.error("State get failed: store=%s key=%s error=%s", store_name, key, exc)
            return None

    async def delete_state(self, store_name: str, key: str) -> bool:
        """
        Delete a key from a Dapr state store.

        URL: DELETE /v1.0/state/{storename}/{key}
        """
        try:
            resp = await self._client.delete(f"/v1.0/state/{store_name}/{key}")
            return resp.status_code in (200, 204)
        except httpx.HTTPError as exc:
            logger.error("State delete failed: store=%s key=%s error=%s", store_name, key, exc)
            return False

    # =====================================================================
    # SECRETS STORE — retrieve secrets via Dapr
    # API: /v1.0/secrets/{storename}/{key}
    # =====================================================================

    async def get_secret(
        self, store_name: str, secret_name: str, key: Optional[str] = None
    ) -> Optional[dict]:
        """
        Retrieve a secret from a Dapr secrets store.

        URL: GET /v1.0/secrets/{storename}/{key}
        Returns dict of secret key-value pairs, or None on failure.
        """
        try:
            resp = await self._client.get(f"/v1.0/secrets/{store_name}/{secret_name}")
            if resp.status_code == 200:
                data = resp.json()
                if key:
                    return data.get(key)
                return data
            return None
        except httpx.HTTPError as exc:
            logger.error(
                "Secret get failed: store=%s name=%s error=%s", store_name, secret_name, exc
            )
            return None

    # =====================================================================
    # SERVICE INVOCATION — call other Dapr apps
    # API: /v1.0/invoke/{appId}/method/{method-name}
    # =====================================================================

    async def invoke_service(
        self,
        app_id: str,
        method: str,
        http_method: str = "GET",
        data: Optional[dict] = None,
        headers: Optional[dict] = None,
    ) -> Optional[httpx.Response]:
        """
        Invoke a method on another Dapr app via service invocation.

        URL: /v1.0/invoke/{appId}/method/{method-name}

        This replaces direct HTTP calls between services. Dapr handles:
          - Service discovery (no hardcoded URLs)
          - mTLS encryption
          - Retries and circuit breaking
          - Load balancing across replicas
        """
        url = f"/v1.0/invoke/{app_id}/method/{method}"
        try:
            if http_method.upper() == "GET":
                resp = await self._client.get(url, headers=headers)
            elif http_method.upper() == "POST":
                resp = await self._client.post(url, json=data, headers=headers)
            elif http_method.upper() == "PUT":
                resp = await self._client.put(url, json=data, headers=headers)
            elif http_method.upper() == "DELETE":
                resp = await self._client.delete(url, headers=headers)
            else:
                resp = await self._client.request(http_method.upper(), url, json=data, headers=headers)
            return resp
        except httpx.HTTPError as exc:
            logger.error(
                "Service invocation failed: app=%s method=%s error=%s", app_id, method, exc
            )
            return None

    # =====================================================================
    # JOBS API — schedule one-time or recurring jobs
    # API: /v1.0-alpha1/jobs/{name}
    #
    # Used for reminder scheduling. When the job fires, Dapr calls:
    #   POST http://localhost:{app-port}/job/{name}
    # =====================================================================

    async def schedule_job(
        self,
        job_name: str,
        data: dict,
        due_time: Optional[str] = None,
        schedule: Optional[str] = None,
        repeats: Optional[int] = None,
        ttl: Optional[str] = None,
    ) -> bool:
        """
        Schedule a one-time or recurring job via Dapr Jobs API.

        Args:
            job_name:  Unique job identifier (e.g., "reminder-{reminder_id}")
            data:      Payload delivered when the job fires
            due_time:  ISO 8601 timestamp for one-time jobs (e.g., "2026-02-10T09:30:00Z")
            schedule:  Cron expression for recurring jobs (e.g., "@every 5m")
            repeats:   Number of times to repeat (None = no limit for scheduled jobs)
            ttl:       Time-to-live duration (e.g., "24h")

        URL: POST /v1.0-alpha1/jobs/{name}

        When the job fires, Dapr POSTs to:
            http://localhost:{app-port}/job/{name}
        The backend must have a handler at that route.
        """
        payload: dict[str, Any] = {"data": data}
        if due_time:
            payload["dueTime"] = due_time
        if schedule:
            payload["schedule"] = schedule
        if repeats is not None:
            payload["repeats"] = repeats
        if ttl:
            payload["ttl"] = ttl

        try:
            resp = await self._client.post(
                f"/v1.0-alpha1/jobs/{job_name}",
                json=payload,
            )
            if resp.status_code in (200, 204):
                logger.info("Job scheduled: name=%s due_time=%s", job_name, due_time)
                return True
            else:
                logger.warning(
                    "Job schedule non-200: name=%s status=%d body=%s",
                    job_name,
                    resp.status_code,
                    resp.text[:200],
                )
                return False
        except httpx.HTTPError as exc:
            logger.error("Job schedule failed: name=%s error=%s", job_name, exc)
            return False

    async def delete_job(self, job_name: str) -> bool:
        """
        Cancel a scheduled job.

        URL: DELETE /v1.0-alpha1/jobs/{name}
        """
        try:
            resp = await self._client.delete(f"/v1.0-alpha1/jobs/{job_name}")
            if resp.status_code in (200, 204):
                logger.info("Job cancelled: name=%s", job_name)
                return True
            return False
        except httpx.HTTPError as exc:
            logger.error("Job cancel failed: name=%s error=%s", job_name, exc)
            return False

    async def get_job(self, job_name: str) -> Optional[dict]:
        """
        Get job details.

        URL: GET /v1.0-alpha1/jobs/{name}
        """
        try:
            resp = await self._client.get(f"/v1.0-alpha1/jobs/{job_name}")
            if resp.status_code == 200:
                return resp.json()
            return None
        except httpx.HTTPError as exc:
            logger.error("Job get failed: name=%s error=%s", job_name, exc)
            return None

    # =====================================================================
    # HEALTH CHECK — verify Dapr sidecar readiness
    # API: /v1.0/healthz
    # =====================================================================

    async def health_check(self) -> bool:
        """
        Check if the Dapr sidecar is healthy and ready.

        URL: GET /v1.0/healthz
        Returns True if sidecar responds 200/204, False otherwise.
        """
        try:
            resp = await self._client.get("/v1.0/healthz")
            return resp.status_code in (200, 204)
        except httpx.HTTPError:
            return False

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------
_dapr_client: Optional[DaprClient] = None


def get_dapr_client() -> DaprClient:
    """Get or create the singleton DaprClient."""
    global _dapr_client
    if _dapr_client is None:
        _dapr_client = DaprClient()
    return _dapr_client
