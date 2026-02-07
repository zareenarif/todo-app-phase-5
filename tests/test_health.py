"""
Test cases for health check and root endpoints.
"""
import pytest
from fastapi import status


class TestHealthEndpoints:
    """Test cases for health and root endpoints."""

    def test_root_endpoint(self, client):
        """TC-HEALTH-001: Root endpoint should return API info."""
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["version"] == "2.0.0"

    def test_health_endpoint(self, client):
        """TC-HEALTH-002: Health endpoint should return healthy status."""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"

    def test_docs_endpoint(self, client):
        """TC-HEALTH-003: API docs should be accessible."""
        response = client.get("/docs")
        assert response.status_code == status.HTTP_200_OK

    def test_redoc_endpoint(self, client):
        """TC-HEALTH-004: ReDoc should be accessible."""
        response = client.get("/redoc")
        assert response.status_code == status.HTTP_200_OK
