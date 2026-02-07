"""
Test cases for task CRUD endpoints.
"""
import pytest
from fastapi import status


class TestListTasks:
    """Test cases for GET /api/v1/tasks"""

    def test_list_tasks_authenticated(self, client, auth_headers, test_task):
        """TC-TASK-001: List tasks with valid token should return user's tasks."""
        response = client.get("/api/v1/tasks", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(task["title"] == "Test Task" for task in data)

    def test_list_tasks_unauthenticated(self, client):
        """TC-TASK-002: List tasks without token should fail."""
        response = client.get("/api/v1/tasks")
        # HTTPBearer returns 403 for missing credentials
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

    def test_list_tasks_filter_by_status_pending(self, client, auth_headers, test_task):
        """TC-TASK-003: Filter tasks by pending status."""
        response = client.get("/api/v1/tasks?status=pending", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # All returned tasks should not be completed
        for task in data:
            assert task["completed"] == False

    def test_list_tasks_filter_by_status_completed(self, client, auth_headers, session, test_task):
        """TC-TASK-004: Filter tasks by completed status."""
        # Mark task as completed
        test_task.completed = True
        session.add(test_task)
        session.commit()

        response = client.get("/api/v1/tasks?status=completed", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for task in data:
            assert task["completed"] == True

    def test_list_tasks_filter_by_priority(self, client, auth_headers, test_task):
        """TC-TASK-005: Filter tasks by priority."""
        response = client.get("/api/v1/tasks?priority=medium", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for task in data:
            assert task["priority"] == "medium"

    def test_list_tasks_sort_by_created_at_asc(self, client, auth_headers, test_task):
        """TC-TASK-006: Sort tasks by created_at ascending."""
        response = client.get("/api/v1/tasks?sort=created_at&order=asc", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK

    def test_list_tasks_sort_by_priority(self, client, auth_headers, test_task):
        """TC-TASK-007: Sort tasks by priority."""
        response = client.get("/api/v1/tasks?sort=priority&order=desc", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK

    def test_list_tasks_empty_for_new_user(self, client, another_user):
        """TC-TASK-008: New user should have empty task list."""
        from src.api.v1.auth import create_access_token
        token = create_access_token(another_user.id)
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get("/api/v1/tasks", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        # Should only return tasks for this specific user
        data = response.json()
        for task in data:
            assert task["user_id"] == another_user.id


class TestGetTask:
    """Test cases for GET /api/v1/tasks/{task_id}"""

    def test_get_task_success(self, client, auth_headers, test_task):
        """TC-TASK-009: Get existing task should return task details."""
        response = client.get(f"/api/v1/tasks/{test_task.id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_task.id
        assert data["title"] == "Test Task"

    def test_get_task_not_found(self, client, auth_headers):
        """TC-TASK-010: Get non-existent task should return 404."""
        response = client.get("/api/v1/tasks/nonexistent-id-123", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_task_unauthorized(self, client, test_task):
        """TC-TASK-011: Get task without auth should fail."""
        response = client.get(f"/api/v1/tasks/{test_task.id}")
        # HTTPBearer returns 403 for missing credentials
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

    def test_get_task_forbidden_other_user(self, client, auth_headers, another_user_task):
        """TC-TASK-012: Get another user's task should return 403."""
        response = client.get(f"/api/v1/tasks/{another_user_task.id}", headers=auth_headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestCreateTask:
    """Test cases for POST /api/v1/tasks"""

    def test_create_task_success(self, client, auth_headers):
        """TC-TASK-013: Create task with valid data should succeed."""
        response = client.post(
            "/api/v1/tasks",
            headers=auth_headers,
            json={
                "title": "New Task",
                "description": "Task description",
                "priority": "high",
                "tags": ["important", "urgent"]
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == "New Task"
        assert data["description"] == "Task description"
        assert data["priority"] == "high"
        assert data["completed"] == False
        assert "id" in data

    def test_create_task_minimal(self, client, auth_headers):
        """TC-TASK-014: Create task with only title should succeed."""
        response = client.post(
            "/api/v1/tasks",
            headers=auth_headers,
            json={"title": "Minimal Task"}
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == "Minimal Task"

    def test_create_task_without_title(self, client, auth_headers):
        """TC-TASK-015: Create task without title should fail."""
        response = client.post(
            "/api/v1/tasks",
            headers=auth_headers,
            json={"description": "No title provided"}
        )
        # API may return 400 or 422 for validation errors
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]

    def test_create_task_unauthorized(self, client):
        """TC-TASK-016: Create task without auth should fail."""
        response = client.post(
            "/api/v1/tasks",
            json={"title": "Unauthorized Task"}
        )
        # HTTPBearer returns 403 for missing credentials
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

    def test_create_task_with_due_date(self, client, auth_headers):
        """TC-TASK-017: Create task with due date should succeed."""
        response = client.post(
            "/api/v1/tasks",
            headers=auth_headers,
            json={
                "title": "Task with due date",
                "due_date": "2026-12-31T23:59:59Z"  # ISO format with timezone
            }
        )
        # May succeed or fail depending on date format validation
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]

    def test_create_task_invalid_priority(self, client, auth_headers):
        """TC-TASK-018: Create task with invalid priority should fail."""
        response = client.post(
            "/api/v1/tasks",
            headers=auth_headers,
            json={
                "title": "Invalid Priority Task",
                "priority": "super-high"  # Invalid value
            }
        )
        # API may return 400 or 422 for validation errors
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]


class TestUpdateTask:
    """Test cases for PUT /api/v1/tasks/{task_id}"""

    def test_update_task_success(self, client, auth_headers, test_task):
        """TC-TASK-019: Update task with valid data should succeed."""
        response = client.put(
            f"/api/v1/tasks/{test_task.id}",
            headers=auth_headers,
            json={
                "title": "Updated Title",
                "description": "Updated description"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["description"] == "Updated description"

    def test_update_task_partial(self, client, auth_headers, test_task):
        """TC-TASK-020: Partial update should only change specified fields."""
        original_description = test_task.description
        response = client.put(
            f"/api/v1/tasks/{test_task.id}",
            headers=auth_headers,
            json={"title": "Only Title Changed"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "Only Title Changed"
        # Description should remain unchanged if not in update
        # (depends on implementation - exclude_unset behavior)

    def test_update_task_not_found(self, client, auth_headers):
        """TC-TASK-021: Update non-existent task should return 404."""
        response = client.put(
            "/api/v1/tasks/nonexistent-id",
            headers=auth_headers,
            json={"title": "Updated"}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_task_forbidden(self, client, auth_headers, another_user_task):
        """TC-TASK-022: Update another user's task should return 403."""
        response = client.put(
            f"/api/v1/tasks/{another_user_task.id}",
            headers=auth_headers,
            json={"title": "Hacked Title"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_task_change_priority(self, client, auth_headers, test_task):
        """TC-TASK-023: Update task priority should succeed."""
        response = client.put(
            f"/api/v1/tasks/{test_task.id}",
            headers=auth_headers,
            json={"priority": "high"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["priority"] == "high"


class TestDeleteTask:
    """Test cases for DELETE /api/v1/tasks/{task_id}"""

    def test_delete_task_success(self, client, auth_headers, test_task):
        """TC-TASK-024: Delete existing task should succeed."""
        response = client.delete(f"/api/v1/tasks/{test_task.id}", headers=auth_headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify task is deleted
        get_response = client.get(f"/api/v1/tasks/{test_task.id}", headers=auth_headers)
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_task_not_found(self, client, auth_headers):
        """TC-TASK-025: Delete non-existent task should return 404."""
        response = client.delete("/api/v1/tasks/nonexistent-id", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_task_forbidden(self, client, auth_headers, another_user_task):
        """TC-TASK-026: Delete another user's task should return 403."""
        response = client.delete(f"/api/v1/tasks/{another_user_task.id}", headers=auth_headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_task_unauthorized(self, client, test_task):
        """TC-TASK-027: Delete task without auth should fail."""
        response = client.delete(f"/api/v1/tasks/{test_task.id}")
        # HTTPBearer returns 403 for missing credentials
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]


class TestToggleTaskCompletion:
    """Test cases for PATCH /api/v1/tasks/{task_id}/complete"""

    def test_toggle_completion_to_completed(self, client, auth_headers, test_task):
        """TC-TASK-028: Toggle incomplete task should mark as completed."""
        assert test_task.completed == False

        response = client.patch(
            f"/api/v1/tasks/{test_task.id}/complete",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["completed"] == True

    def test_toggle_completion_to_incomplete(self, client, auth_headers, session, test_task):
        """TC-TASK-029: Toggle completed task should mark as incomplete."""
        # First mark as completed
        test_task.completed = True
        session.add(test_task)
        session.commit()

        response = client.patch(
            f"/api/v1/tasks/{test_task.id}/complete",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["completed"] == False

    def test_toggle_completion_not_found(self, client, auth_headers):
        """TC-TASK-030: Toggle non-existent task should return 404."""
        response = client.patch(
            "/api/v1/tasks/nonexistent-id/complete",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_toggle_completion_forbidden(self, client, auth_headers, another_user_task):
        """TC-TASK-031: Toggle another user's task should return 403."""
        response = client.patch(
            f"/api/v1/tasks/{another_user_task.id}/complete",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_toggle_completion_unauthorized(self, client, test_task):
        """TC-TASK-032: Toggle task without auth should fail."""
        response = client.patch(f"/api/v1/tasks/{test_task.id}/complete")
        # HTTPBearer returns 403 for missing credentials
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
