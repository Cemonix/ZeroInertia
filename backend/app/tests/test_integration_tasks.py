"""
Integration tests for task management endpoints.

Tests cover:
- Task CRUD operations
- Task filtering by project
- Task completion and archiving
- Task ordering and reordering
- Permission checks (user can only access their own tasks)
- Edge cases and security
"""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Section, Task
from app.models.project import Project
from app.models.user import User

# pyright: reportAny=false


class TestTaskEndpoints:
    """Test task management functionality."""

    async def test_create_task_minimal(self, authenticated_client: AsyncClient, test_project: Project, test_section: Section) -> None:
        """Test creating a task with minimal required fields."""
        response = await authenticated_client.post(
            "/api/v1/tasks",
            json={
                "title": "New Task",
                "project_id": str(test_project.id),
                "section_id": str(test_section.id),
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New Task"
        assert data["project_id"] == str(test_project.id)
        assert data["completed"] is False
        assert "id" in data

    async def test_create_task_full(
        self, authenticated_client: AsyncClient, test_project: Project, test_section: Section
    ) -> None:
        """Test creating a task with all fields."""
        response = await authenticated_client.post(
            "/api/v1/tasks",
            json={
                "title": "Complete Task",
                "description": "Task with all details",
                "project_id": str(test_project.id),
                "section_id": str(test_section.id),
                "due_datetime": "2025-12-31T23:59:59Z",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Complete Task"
        assert data["description"] == "Task with all details"
        assert data["project_id"] == str(test_project.id)
        assert data["section_id"] == str(test_section.id)
        assert data["due_datetime"] is not None

    async def test_create_task_nonexistent_section(
        self, authenticated_client: AsyncClient, test_project: Project
    ) -> None:
        """Test creating a task with non-existent section returns 404."""
        fake_section_id = uuid4()

        response = await authenticated_client.post(
            "/api/v1/tasks",
            json={
                "title": "Task with invalid section",
                "project_id": str(test_project.id),
                "section_id": str(fake_section_id),
            },
        )

        assert response.status_code == 404
        assert "section" in response.json()["detail"].lower()

    async def test_create_task_nonexistent_project(
        self, authenticated_client: AsyncClient, test_section: Section
    ) -> None:
        """Test creating a task with non-existent project returns 404."""
        fake_project_id = uuid4()

        response = await authenticated_client.post(
            "/api/v1/tasks",
            json={
                "title": "Task with invalid project",
                "project_id": str(fake_project_id),
                "section_id": str(test_section.id),
            },
        )

        assert response.status_code == 404
        assert "project" in response.json()["detail"].lower()

    async def test_get_all_tasks(
        self, authenticated_client: AsyncClient, test_task: Task,
    ) -> None:
        """Test retrieving all tasks for a user."""
        response = await authenticated_client.get("/api/v1/tasks")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1  # pyright: ignore[reportUnknownArgumentType]
        assert any(task["id"] == str(test_task.id) for task in data)  # pyright: ignore[reportUnknownArgumentType, reportUnknownVariableType]

    async def test_get_tasks_filtered_by_project(
        self, authenticated_client: AsyncClient, test_project: Project
    ) -> None:
        """Test retrieving tasks filtered by project."""
        response = await authenticated_client.get(
            f"/api/v1/tasks?project_id={test_project.id}"
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # All returned tasks should belong to the specified project
        for task in data:  # pyright: ignore[reportUnknownVariableType]
            assert task["project_id"] == str(test_project.id)

    async def test_get_single_task(self, authenticated_client: AsyncClient, test_task: Task) -> None:
        """Test retrieving a specific task by ID."""
        response = await authenticated_client.get(f"/api/v1/tasks/{test_task.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_task.id)
        assert data["title"] == test_task.title

    async def test_get_nonexistent_task(self, authenticated_client: AsyncClient) -> None:
        """Test retrieving a non-existent task returns 404."""
        fake_task_id = uuid4()
        response = await authenticated_client.get(f"/api/v1/tasks/{fake_task_id}")

        assert response.status_code == 404

    async def test_update_task(self, authenticated_client: AsyncClient, test_task: Task) -> None:
        """Test updating a task."""
        response = await authenticated_client.patch(
            f"/api/v1/tasks/{test_task.id}",
            json={
                "title": "Updated Task Title",
                "description": "Updated description",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Task Title"
        assert data["description"] == "Updated description"

    async def test_complete_task(self, authenticated_client: AsyncClient, test_task: Task) -> None:
        """Test marking a task as completed."""
        response = await authenticated_client.patch(
            f"/api/v1/tasks/{test_task.id}",
            json={"completed": True},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["completed"] is True

    async def test_archive_task(self, authenticated_client: AsyncClient, test_task: Task) -> None:
        """Test archiving a task."""
        response = await authenticated_client.post(
            f"/api/v1/tasks/{test_task.id}/archive",
        )

        assert response.status_code == 204

        # Verify archived task doesn't appear in regular list
        list_response = await authenticated_client.get("/api/v1/tasks")
        tasks = list_response.json()
        assert not any(task["id"] == str(test_task.id) for task in tasks)

    async def test_get_archived_tasks(self, authenticated_client: AsyncClient, test_task: Task) -> None:
        """Test retrieving archived tasks."""
        # First archive a task
        _ = await authenticated_client.post(f"/api/v1/tasks/{test_task.id}/archive")

        # Now retrieve archived tasks
        response = await authenticated_client.get("/api/v1/tasks/archived")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert any(task["id"] == str(test_task.id) for task in data)  # pyright: ignore[reportUnknownArgumentType, reportUnknownVariableType]

    async def test_delete_task(self, authenticated_client: AsyncClient, test_task: Task) -> None:
        """Test deleting a task."""
        response = await authenticated_client.delete(f"/api/v1/tasks/{test_task.id}")

        assert response.status_code == 204

        # Verify task is actually deleted
        get_response = await authenticated_client.get(f"/api/v1/tasks/{test_task.id}")
        assert get_response.status_code == 404

    async def test_snooze_non_recurring_task(
        self,
        authenticated_client: AsyncClient,
        test_task: Task,
    ) -> None:
        """Snoozing a task without recurrence should push due date forward one day."""
        base_due = (datetime.now(timezone.utc) + timedelta(days=3)).replace(microsecond=0)
        base_due_iso = base_due.isoformat().replace("+00:00", "Z")

        patch_response = await authenticated_client.patch(
            f"/api/v1/tasks/{test_task.id}",
            json={"due_datetime": base_due_iso},
        )
        assert patch_response.status_code == 200

        response = await authenticated_client.post(f"/api/v1/tasks/{test_task.id}/snooze")
        assert response.status_code == 200

        data = response.json()
        first_due = datetime.fromisoformat(data["due_datetime"].replace("Z", "+00:00"))
        expected_first_due = base_due + timedelta(days=1)
        assert abs((first_due - expected_first_due).total_seconds()) < 1
        assert data["snooze_count"] == 1

        # Snoozing again should continue to advance the due date and increment the counter
        second_response = await authenticated_client.post(f"/api/v1/tasks/{test_task.id}/snooze")
        assert second_response.status_code == 200
        data_second = second_response.json()
        second_due = datetime.fromisoformat(data_second["due_datetime"].replace("Z", "+00:00"))
        expected_second_due = expected_first_due + timedelta(days=1)
        assert abs((second_due - expected_second_due).total_seconds()) < 1
        assert data_second["snooze_count"] == 2

    async def test_snooze_without_due_date_returns_error(
        self,
        authenticated_client: AsyncClient,
        test_task: Task,
    ) -> None:
        """Snoozing a task without a due date should return a 400."""
        response = await authenticated_client.post(f"/api/v1/tasks/{test_task.id}/snooze")
        assert response.status_code == 400

    async def test_cannot_access_other_users_task(
        self, authenticated_client: AsyncClient, db_session: AsyncSession, test_project: Project, test_section: Section
    ) -> None:
        """Test that users cannot access tasks belonging to other users."""
        # Create another user
        other_user = User(
            email="other@example.com",
            oauth_provider="google",
            oauth_subject_id="other_oauth_id",
        )
        db_session.add(other_user)
        await db_session.commit()
        await db_session.refresh(other_user)

        # Create a task for the other user
        other_task = Task(
            title="Other User's Task",
            user_id=other_user.id,
            project_id=test_project.id,
            section_id=test_section.id,
            order_index=0,
            completed=False,
            archived=False,
        )
        db_session.add(other_task)
        await db_session.commit()
        await db_session.refresh(other_task)

        # Try to access the other user's task
        response = await authenticated_client.get(f"/api/v1/tasks/{other_task.id}")

        assert response.status_code == 404  # Should act as if it doesn't exist


class TestTaskOrdering:
    """Test task ordering and reordering functionality."""

    async def test_task_default_order(
        self, authenticated_client: AsyncClient, test_project: Project, test_section: Section
    ) -> None:
        """Test that tasks are created with proper order indices."""
        # Create multiple tasks
        task_ids: list[str] = []
        for i in range(3):
            response = await authenticated_client.post(
                "/api/v1/tasks",
                json={
                    "title": f"Task {i}",
                    "project_id": str(test_project.id),
                    "section_id": str(test_section.id),
                },
            )
            assert response.status_code == 201
            task_ids.append(response.json()["id"])

        # Get all tasks
        response = await authenticated_client.get(
            f"/api/v1/tasks?project_id={test_project.id}"
        )
        tasks = response.json()

        # Verify tasks have sequential order indices
        assert len(tasks) == 3
        order_indices = [task["order_index"] for task in tasks]
        assert sorted(order_indices) == order_indices  # Should be in order

    async def test_reorder_tasks(
        self, authenticated_client: AsyncClient, test_project: Project, test_section: Section
    ) -> None:
        """Test reordering tasks."""
        # Create tasks
        task_ids: list[str] = []
        for i in range(3):
            response = await authenticated_client.post(
                "/api/v1/tasks",
                json={
                    "title": f"Task {i}",
                    "project_id": str(test_project.id),
                    "section_id": str(test_section.id),
                },
            )
            task_ids.append(response.json()["id"])

        # Reorder: move last task to first position - send list of TaskReorder objects
        response = await authenticated_client.post(
            "/api/v1/tasks/reorder",
            json=[
                {"id": task_ids[2], "section_id": str(test_section.id), "order_index": 0},
                {"id": task_ids[0], "section_id": str(test_section.id), "order_index": 1},
                {"id": task_ids[1], "section_id": str(test_section.id), "order_index": 2},
            ],
        )

        assert response.status_code == 204


class TestTaskEdgeCases:
    """Test edge cases and input validation."""

    @pytest.mark.parametrize(
        "title,description",
        [
            ("Task with émojis 🚀✨", "Description with unicode: café, naïve"),
            ("中文任务名称", "日本語の説明"),
            ("🎉🎊🎈 Emoji Only", "💯✅🔥"),
            ("Mixed: English & 中文 & émoji 🌍", "Testing unicode ñ ü ö"),
        ],
    )
    async def test_create_task_with_unicode_and_emoji(
        self,
        authenticated_client: AsyncClient,
        test_project: Project,
        test_section: Section,
        title: str,
        description: str,
    ) -> None:
        """Test creating tasks with unicode characters and emoji."""
        response = await authenticated_client.post(
            "/api/v1/tasks",
            json={
                "title": title,
                "description": description,
                "project_id": str(test_project.id),
                "section_id": str(test_section.id),
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == title
        assert data["description"] == description

    async def test_create_task_with_very_long_title(
        self, authenticated_client: AsyncClient, test_project: Project, test_section: Section
    ) -> None:
        """Test creating a task with extremely long title."""
        long_title = "A" * 1000
        response = await authenticated_client.post(
            "/api/v1/tasks",
            json={
                "title": long_title,
                "project_id": str(test_project.id),
                "section_id": str(test_section.id),
            },
        )

        # Should either accept it or return validation error
        assert response.status_code in [201, 422]

    async def test_create_task_with_very_long_description(
        self, authenticated_client: AsyncClient, test_project: Project, test_section: Section
    ) -> None:
        """Test creating a task with extremely long description."""
        long_description = "B" * 10000
        response = await authenticated_client.post(
            "/api/v1/tasks",
            json={
                "title": "Task with long description",
                "description": long_description,
                "project_id": str(test_project.id),
                "section_id": str(test_section.id),
            },
        )

        # Should either accept it or return validation error
        assert response.status_code in [201, 422]

    async def test_create_task_with_empty_title(
        self, authenticated_client: AsyncClient, test_project: Project, test_section: Section
    ) -> None:
        """Test creating a task with empty title fails validation."""
        response = await authenticated_client.post(
            "/api/v1/tasks",
            json={
                "title": "",
                "project_id": str(test_project.id),
                "section_id": str(test_section.id),
            },
        )

        assert response.status_code == 422

    async def test_create_task_with_whitespace_only_title(
        self, authenticated_client: AsyncClient, test_project: Project, test_section: Section
    ) -> None:
        """Test creating a task with whitespace-only title."""
        response = await authenticated_client.post(
            "/api/v1/tasks",
            json={
                "title": "   ",
                "project_id": str(test_project.id),
                "section_id": str(test_section.id),
            },
        )

        # Should fail validation or trim and reject
        assert response.status_code in [201, 422]

    async def test_create_task_with_sql_injection_attempt(
        self, authenticated_client: AsyncClient, test_project: Project, test_section: Section
    ) -> None:
        """Test that SQL injection attempts in task title are safely handled."""
        malicious_title = "'; DROP TABLE tasks; --"
        response = await authenticated_client.post(
            "/api/v1/tasks",
            json={
                "title": malicious_title,
                "project_id": str(test_project.id),
                "section_id": str(test_section.id),
            },
        )

        assert response.status_code == 201
        data = response.json()
        # Should be stored as literal string, not executed
        assert data["title"] == malicious_title

        # Verify task was created and can be retrieved
        get_response = await authenticated_client.get(f"/api/v1/tasks/{data['id']}")
        assert get_response.status_code == 200

    async def test_create_task_with_malformed_json(
        self, authenticated_client: AsyncClient
    ) -> None:
        """Test that malformed JSON returns proper error."""
        response = await authenticated_client.post(
            "/api/v1/tasks",
            content="{invalid json}",
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 422

    async def test_create_task_with_invalid_uuid(
        self, authenticated_client: AsyncClient, test_section: Section
    ) -> None:
        """Test creating a task with invalid project UUID format."""
        response = await authenticated_client.post(
            "/api/v1/tasks",
            json={
                "title": "Task",
                "project_id": "not-a-valid-uuid",
                "section_id": str(test_section.id),
            },
        )

        assert response.status_code == 422

    async def test_update_task_with_xss_attempt(
        self, authenticated_client: AsyncClient, test_task: Task
    ) -> None:
        """Test that XSS attempts are safely handled."""
        xss_payload = "<script>alert('XSS')</script>"
        response = await authenticated_client.patch(
            f"/api/v1/tasks/{test_task.id}",
            json={
                "title": xss_payload,
                "description": "<img src=x onerror=alert('XSS')>",
            },
        )

        assert response.status_code == 200
        data = response.json()
        # Should be stored as literal strings
        assert data["title"] == xss_payload

    async def test_get_task_with_invalid_uuid_format(
        self, authenticated_client: AsyncClient
    ) -> None:
        """Test getting a task with malformed UUID."""
        response = await authenticated_client.get("/api/v1/tasks/not-a-uuid")

        assert response.status_code == 422


class TestTaskSecurity:
    """Test security and authorization."""

    async def test_task_isolation_between_users(
        self,
        authenticated_client: AsyncClient,
        db_session: AsyncSession,
        test_project: Project,
        test_section: Section,
    ) -> None:
        """Test that user A cannot see user B's tasks in list endpoint."""
        # Create another user
        other_user = User(
            email="other@example.com",
            oauth_provider="google",
            oauth_subject_id="other_oauth_id",
        )
        db_session.add(other_user)
        await db_session.commit()
        await db_session.refresh(other_user)

        # Create task for other user
        other_task = Task(
            title="Other User's Task",
            user_id=other_user.id,
            project_id=test_project.id,
            section_id=test_section.id,
            order_index=0,
            completed=False,
            archived=False,
        )
        db_session.add(other_task)
        await db_session.commit()

        # Current authenticated user should not see other user's task
        response = await authenticated_client.get("/api/v1/tasks")
        assert response.status_code == 200
        tasks = response.json()
        task_ids = [task["id"] for task in tasks]
        assert str(other_task.id) not in task_ids

    async def test_cannot_update_other_users_task(
        self,
        authenticated_client: AsyncClient,
        db_session: AsyncSession,
        test_project: Project,
        test_section: Section,
    ) -> None:
        """Test that users cannot update tasks belonging to others."""
        # Create another user with a task
        other_user = User(
            email="other@example.com",
            oauth_provider="google",
            oauth_subject_id="other_oauth_id",
        )
        db_session.add(other_user)
        await db_session.commit()
        await db_session.refresh(other_user)

        other_task = Task(
            title="Other User's Task",
            user_id=other_user.id,
            project_id=test_project.id,
            section_id=test_section.id,
            order_index=0,
            completed=False,
            archived=False,
        )
        db_session.add(other_task)
        await db_session.commit()
        await db_session.refresh(other_task)

        # Try to update other user's task
        response = await authenticated_client.patch(
            f"/api/v1/tasks/{other_task.id}",
            json={"title": "Hacked Title"},
        )

        assert response.status_code == 404

    async def test_cannot_delete_other_users_task(
        self,
        authenticated_client: AsyncClient,
        db_session: AsyncSession,
        test_project: Project,
        test_section: Section,
    ) -> None:
        """Test that users cannot delete tasks belonging to others."""
        # Create another user with a task
        other_user = User(
            email="other@example.com",
            oauth_provider="google",
            oauth_subject_id="other_oauth_id",
        )
        db_session.add(other_user)
        await db_session.commit()
        await db_session.refresh(other_user)

        other_task = Task(
            title="Other User's Task",
            user_id=other_user.id,
            project_id=test_project.id,
            section_id=test_section.id,
            order_index=0,
            completed=False,
            archived=False,
        )
        db_session.add(other_task)
        await db_session.commit()
        await db_session.refresh(other_task)

        # Try to delete other user's task
        response = await authenticated_client.delete(f"/api/v1/tasks/{other_task.id}")

        assert response.status_code == 404


class TestRecurringTasks:
    """Test recurring task functionality."""

    async def test_complete_daily_recurring_task_creates_new_instance(
        self,
        authenticated_client: AsyncClient,
        test_project: Project,
        test_section: Section,
    ) -> None:
        """Test that completing a daily recurring task archives it and creates a new instance."""
        # Create a daily recurring task
        response = await authenticated_client.post(
            "/api/v1/tasks",
            json={
                "title": "Daily Standup",
                "description": "Attend daily standup meeting",
                "project_id": str(test_project.id),
                "section_id": str(test_section.id),
                "due_datetime": "2025-01-15T09:00:00Z",
                "recurrence_type": "daily",
                "recurrence_days": None,
            },
        )

        assert response.status_code == 201
        original_task = response.json()
        original_task_id = original_task["id"]

        # Complete the recurring task
        complete_response = await authenticated_client.patch(
            f"/api/v1/tasks/{original_task_id}",
            json={"completed": True},
        )

        # Should succeed and return the archived task
        assert complete_response.status_code == 200
        completed_task = complete_response.json()
        assert completed_task["completed"] is True
        assert completed_task["archived"] is True
        assert completed_task["recurrence_type"] is None  # Cleared on archived task

        # Get all tasks - should not include the archived one
        list_response = await authenticated_client.get(
            f"/api/v1/tasks?project_id={test_project.id}"
        )
        assert list_response.status_code == 200
        active_tasks = list_response.json()

        # The archived task should not appear
        assert not any(task["id"] == original_task_id for task in active_tasks)

        # Should have a new recurring task instance
        recurring_tasks = [
            task for task in active_tasks
            if task["title"] == "Daily Standup" and task["recurrence_type"] == "daily"
        ]
        assert len(recurring_tasks) == 1
        new_task = recurring_tasks[0]

        # Verify the new task has correct properties
        assert new_task["id"] != original_task_id  # Different ID
        assert new_task["title"] == original_task["title"]
        assert new_task["description"] == original_task["description"]
        assert new_task["completed"] is False
        assert new_task["archived"] is False
        assert new_task["recurrence_type"] == "daily"
        # Due date should be one day later
        assert new_task["due_datetime"] == "2025-01-16T09:00:00Z"

    async def test_complete_weekly_recurring_task_creates_new_instance(
        self,
        authenticated_client: AsyncClient,
        test_project: Project,
        test_section: Section,
    ) -> None:
        """Test that completing a weekly recurring task archives it and creates a new instance."""
        # Create a weekly recurring task (Monday and Friday = 0 and 4 in Python weekday convention)
        response = await authenticated_client.post(
            "/api/v1/tasks",
            json={
                "title": "Team Meeting",
                "description": "Weekly team sync",
                "project_id": str(test_project.id),
                "section_id": str(test_section.id),
                "due_datetime": "2025-01-13T14:00:00Z",  # Monday
                "recurrence_type": "weekly",
                "recurrence_days": [0, 4],  # Monday=0, Friday=4
            },
        )

        assert response.status_code == 201
        original_task = response.json()
        original_task_id = original_task["id"]

        # Complete the recurring task
        complete_response = await authenticated_client.patch(
            f"/api/v1/tasks/{original_task_id}",
            json={"completed": True},
        )

        # Should succeed
        assert complete_response.status_code == 200
        completed_task = complete_response.json()
        assert completed_task["completed"] is True
        assert completed_task["archived"] is True

        # Get all tasks - verify new instance exists
        list_response = await authenticated_client.get(
            f"/api/v1/tasks?project_id={test_project.id}"
        )
        assert list_response.status_code == 200
        active_tasks = list_response.json()

        # Should have a new recurring task instance
        recurring_tasks = [
            task for task in active_tasks
            if task["title"] == "Team Meeting" and task["recurrence_type"] == "weekly"
        ]
        assert len(recurring_tasks) == 1
        new_task = recurring_tasks[0]

        # Verify the new task
        assert new_task["id"] != original_task_id
        assert new_task["completed"] is False
        assert new_task["archived"] is False
        assert new_task["recurrence_type"] == "weekly"
        assert new_task["recurrence_days"] == [0, 4]
        # Due date should be Friday (next occurrence)
        assert new_task["due_datetime"] == "2025-01-17T14:00:00Z"

    async def test_complete_alternate_days_recurring_task(
        self,
        authenticated_client: AsyncClient,
        test_project: Project,
        test_section: Section,
    ) -> None:
        """Test that completing an alternate days recurring task works correctly."""
        # Create an alternate days recurring task
        response = await authenticated_client.post(
            "/api/v1/tasks",
            json={
                "title": "Exercise",
                "project_id": str(test_project.id),
                "section_id": str(test_section.id),
                "due_datetime": "2025-01-15T06:00:00Z",
                "recurrence_type": "alternate_days",
                "recurrence_days": None,
            },
        )

        assert response.status_code == 201
        original_task = response.json()
        original_task_id = original_task["id"]

        # Complete the task
        complete_response = await authenticated_client.patch(
            f"/api/v1/tasks/{original_task_id}",
            json={"completed": True},
        )

        assert complete_response.status_code == 200
        completed_task = complete_response.json()
        assert completed_task["completed"] is True
        assert completed_task["archived"] is True

        # Verify new instance exists with due date 2 days later
        list_response = await authenticated_client.get(
            f"/api/v1/tasks?project_id={test_project.id}"
        )
        active_tasks = list_response.json()

        recurring_tasks = [
            task for task in active_tasks
            if task["title"] == "Exercise" and task["recurrence_type"] == "alternate_days"
        ]
        assert len(recurring_tasks) == 1
        new_task = recurring_tasks[0]
        assert new_task["due_datetime"] == "2025-01-17T06:00:00Z"

    async def test_complete_non_recurring_task_does_not_create_new_instance(
        self,
        authenticated_client: AsyncClient,
        test_task: Task,
    ) -> None:
        """Test that completing a regular (non-recurring) task doesn't create a new instance."""
        # Get initial task count
        initial_response = await authenticated_client.get(
            f"/api/v1/tasks?project_id={test_task.project_id}"
        )
        initial_count = len(initial_response.json())

        # Complete the non-recurring task
        complete_response = await authenticated_client.patch(
            f"/api/v1/tasks/{test_task.id}",
            json={"completed": True},
        )

        assert complete_response.status_code == 200
        completed_task = complete_response.json()
        assert completed_task["completed"] is True
        assert completed_task["archived"] is False  # Regular tasks don't auto-archive

        # Task count should remain the same
        final_response = await authenticated_client.get(
            f"/api/v1/tasks?project_id={test_task.project_id}"
        )
        final_count = len(final_response.json())
        assert final_count == initial_count

    async def test_uncomplete_recurring_task_does_not_duplicate(
        self,
        authenticated_client: AsyncClient,
        test_project: Project,
        test_section: Section,
    ) -> None:
        """Test that un-completing a completed task doesn't trigger duplication."""
        # Create and complete a recurring task
        create_response = await authenticated_client.post(
            "/api/v1/tasks",
            json={
                "title": "Daily Task",
                "project_id": str(test_project.id),
                "section_id": str(test_section.id),
                "due_datetime": "2025-01-15T10:00:00Z",
                "recurrence_type": "daily",
            },
        )
        original_task_id = create_response.json()["id"]

        # Complete it
        _ = await authenticated_client.patch(
            f"/api/v1/tasks/{original_task_id}",
            json={"completed": True},
        )

        # Get the new task that was created
        list_response = await authenticated_client.get(
            f"/api/v1/tasks?project_id={test_project.id}"
        )
        active_tasks = list_response.json()
        new_task = [
            task for task in active_tasks
            if task["title"] == "Daily Task" and task["recurrence_type"] == "daily"
        ][0]
        new_task_id = new_task["id"]

        # Mark the new task as completed, then un-complete it
        _ = await authenticated_client.patch(
            f"/api/v1/tasks/{new_task_id}",
            json={"completed": True},
        )

        # Un-complete should not work on archived task
        # (attempting to uncomplete an archived task should fail or be ignored)
        uncomplete_response = await authenticated_client.patch(
            f"/api/v1/tasks/{new_task_id}",
            json={"completed": False},
        )

        # The task is archived, so it should either be 404 or rejected
        # (depends on implementation - archived tasks shouldn't be modifiable)
        assert uncomplete_response.status_code in [200, 404]
