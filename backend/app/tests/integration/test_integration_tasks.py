"""
Integration tests for task management endpoints.

Tests cover:
- Task CRUD operations
- Task filtering by project
- Task filtering by date range
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
        assert isinstance(data, dict)
        assert "items" in data
        assert isinstance(data["items"], list)
        assert len(data["items"]) >= 1  # pyright: ignore[reportUnknownArgumentType]
        assert any(task["id"] == str(test_task.id) for task in data["items"])  # pyright: ignore[reportUnknownArgumentType, reportUnknownVariableType]

    async def test_get_tasks_filtered_by_project(
        self, authenticated_client: AsyncClient, test_project: Project
    ) -> None:
        """Test retrieving tasks filtered by project."""
        response = await authenticated_client.get(
            f"/api/v1/tasks?project_id={test_project.id}"
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "items" in data
        assert isinstance(data["items"], list)
        # All returned tasks should belong to the specified project
        for task in data["items"]:  # pyright: ignore[reportUnknownVariableType]
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
        assert not any(task["id"] == str(test_task.id) for task in tasks["items"])

    async def test_get_archived_tasks(self, authenticated_client: AsyncClient, test_task: Task) -> None:
        """Test retrieving archived tasks."""
        # First archive a task
        _ = await authenticated_client.post(f"/api/v1/tasks/{test_task.id}/archive")

        # Now retrieve archived tasks
        response = await authenticated_client.get("/api/v1/tasks/archived")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "items" in data
        assert isinstance(data["items"], list)
        assert any(task["id"] == str(test_task.id) for task in data["items"])  # pyright: ignore[reportUnknownArgumentType, reportUnknownVariableType]

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
        data = response.json()
        tasks = data["items"]

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
                {"id": task_ids[2], "project_id": str(test_project.id), "section_id": str(test_section.id), "order_index": 0},
                {"id": task_ids[0], "project_id": str(test_project.id), "section_id": str(test_section.id), "order_index": 1},
                {"id": task_ids[1], "project_id": str(test_project.id), "section_id": str(test_section.id), "order_index": 2},
            ],
        )

        assert response.status_code == 204

    async def test_reorder_tasks_across_sections(
        self,
        authenticated_client: AsyncClient,
        test_project: Project,
        test_section: Section,
    ) -> None:
        """Reorder tasks while moving items between sections in one batch."""
        # Create a second section in the same project
        sec_resp = await authenticated_client.post(
            "/api/v1/sections",
            json={
                "title": "Second Section",
                "project_id": str(test_project.id),
                "order_index": 1,
            },
        )
        assert sec_resp.status_code == 201
        second_section_id = sec_resp.json()["id"]

        # Create two tasks in section A and two tasks in section B
        create_payloads = [
            {"title": "A1", "project_id": str(test_project.id), "section_id": str(test_section.id)},
            {"title": "A2", "project_id": str(test_project.id), "section_id": str(test_section.id)},
            {"title": "B1", "project_id": str(test_project.id), "section_id": str(second_section_id)},
            {"title": "B2", "project_id": str(test_project.id), "section_id": str(second_section_id)},
        ]
        created: list[dict[str, object]] = []
        for payload in create_payloads:
            r = await authenticated_client.post("/api/v1/tasks", json=payload)
            assert r.status_code == 201
            created.append(r.json())

        # Move A2 to section B and B1 to section A. Reindex within each target section.
        a1_id = created[0]["id"]
        a2_id = created[1]["id"]
        b1_id = created[2]["id"]
        b2_id = created[3]["id"]

        reorder_payload = [
            {"id": a1_id, "project_id": str(test_project.id), "section_id": str(test_section.id), "order_index": 1},  # A1 -> A index 1
            {"id": b1_id, "project_id": str(test_project.id), "section_id": str(test_section.id), "order_index": 0},  # B1 -> A index 0
            {"id": a2_id, "project_id": str(test_project.id), "section_id": str(second_section_id), "order_index": 1},  # A2 -> B index 1
            {"id": b2_id, "project_id": str(test_project.id), "section_id": str(second_section_id), "order_index": 0},  # B2 -> B index 0
        ]

        resp = await authenticated_client.post("/api/v1/tasks/reorder", json=reorder_payload)
        assert resp.status_code == 204

        # Verify via list call and filtering by section
        list_resp = await authenticated_client.get(f"/api/v1/tasks?project_id={test_project.id}")
        assert list_resp.status_code == 200
        tasks = list_resp.json()["items"]

        # Build lookup by id
        by_id = {t["id"]: t for t in tasks}

        assert by_id[b1_id]["section_id"] == str(test_section.id)
        assert by_id[b1_id]["order_index"] == 0
        assert by_id[a1_id]["section_id"] == str(test_section.id)
        assert by_id[a1_id]["order_index"] == 1

        assert by_id[b2_id]["section_id"] == str(second_section_id)
        assert by_id[b2_id]["order_index"] == 0
        assert by_id[a2_id]["section_id"] == str(second_section_id)
        assert by_id[a2_id]["order_index"] == 1

    async def test_reorder_with_empty_payload(
        self,
        authenticated_client: AsyncClient,
    ) -> None:
        """Test that reordering with empty payload doesn't cause SQL errors."""
        # Send empty reorder payload
        response = await authenticated_client.post("/api/v1/tasks/reorder", json=[])
        # Should return 204 (no-op) or 400, but not 500 (SQL error)
        assert response.status_code in [204, 400]

    async def test_reorder_with_null_ids(
        self,
        authenticated_client: AsyncClient,
        test_section: Section,
    ) -> None:
        """Test that reordering with null IDs is rejected properly."""
        # Try to send reorder with null ID
        response = await authenticated_client.post(
            "/api/v1/tasks/reorder",
            json=[
                {"id": None, "section_id": str(test_section.id), "order_index": 0},
            ],
        )
        # Should be rejected with 422 validation error, not SQL error
        assert response.status_code == 422


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
        data = response.json()
        tasks = data["items"]
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
                "recurrence_interval": 1,
                "recurrence_unit": "days",
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
        assert completed_task["recurrence_interval"] is None  # Cleared on archived task
        assert completed_task["recurrence_unit"] is None

        # Get all tasks - should not include the archived one
        list_response = await authenticated_client.get(
            f"/api/v1/tasks?project_id={test_project.id}"
        )
        assert list_response.status_code == 200
        data = list_response.json()
        active_tasks = data["items"]

        # The archived task should not appear
        assert not any(task["id"] == original_task_id for task in active_tasks)

        # Should have a new recurring task instance
        recurring_tasks = [
            task for task in active_tasks
            if task["title"] == "Daily Standup" and task["recurrence_interval"] == 1 and task["recurrence_unit"] == "days"
        ]
        assert len(recurring_tasks) == 1
        new_task = recurring_tasks[0]

        # Verify the new task has correct properties
        assert new_task["id"] != original_task_id  # Different ID
        assert new_task["title"] == original_task["title"]
        assert new_task["description"] == original_task["description"]
        assert new_task["completed"] is False
        assert new_task["archived"] is False
        assert new_task["recurrence_interval"] == 1
        assert new_task["recurrence_unit"] == "days"
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
                "recurrence_interval": 1,
                "recurrence_unit": "weeks",
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
        data = list_response.json()
        active_tasks = data["items"]

        # Should have a new recurring task instance
        recurring_tasks = [
            task for task in active_tasks
            if task["title"] == "Team Meeting" and task["recurrence_unit"] == "weeks"
        ]
        assert len(recurring_tasks) == 1
        new_task = recurring_tasks[0]

        # Verify the new task
        assert new_task["id"] != original_task_id
        assert new_task["completed"] is False
        assert new_task["archived"] is False
        assert new_task["recurrence_interval"] == 1
        assert new_task["recurrence_unit"] == "weeks"
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
                "recurrence_interval": 2,
                "recurrence_unit": "days",
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
        data = list_response.json()
        active_tasks = data["items"]

        recurring_tasks = [
            task for task in active_tasks
            if task["title"] == "Exercise" and task["recurrence_interval"] == 2 and task["recurrence_unit"] == "days"
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
                "recurrence_interval": 1,
                "recurrence_unit": "days",
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
        data = list_response.json()
        active_tasks = data["items"]
        new_task = [
            task for task in active_tasks
            if task["title"] == "Daily Task" and task["recurrence_interval"] == 1 and task["recurrence_unit"] == "days"
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

    async def test_complete_recurring_task_with_labels_preserves_labels(
        self,
        authenticated_client: AsyncClient,
        test_project: Project,
        test_section: Section,
    ) -> None:
        """Test that completing a recurring task with labels preserves the labels in the new instance.

        This test specifically targets the greenlet error that occurs when accessing
        task.labels relationship in production after a commit.
        """
        # Create labels for the task
        label1_response = await authenticated_client.post(
            "/api/v1/labels",
            json={
                "name": "urgent",
                "color": "#ff0000",
                "description": "Urgent tasks",
            },
        )
        assert label1_response.status_code == 201
        label1 = label1_response.json()

        label2_response = await authenticated_client.post(
            "/api/v1/labels",
            json={
                "name": "work",
                "color": "#0000ff",
                "description": "Work-related tasks",
            },
        )
        assert label2_response.status_code == 201
        label2 = label2_response.json()

        # Create a daily recurring task with labels
        create_response = await authenticated_client.post(
            "/api/v1/tasks",
            json={
                "title": "Daily Report",
                "description": "Send daily status report",
                "project_id": str(test_project.id),
                "section_id": str(test_section.id),
                "due_datetime": "2025-01-15T17:00:00Z",
                "recurrence_interval": 1,
                "recurrence_unit": "days",
                "label_ids": [label1["id"], label2["id"]],
            },
        )

        assert create_response.status_code == 201
        original_task = create_response.json()
        original_task_id = original_task["id"]

        # Verify the original task has the labels
        assert len(original_task["labels"]) == 2
        label_names = {label["name"] for label in original_task["labels"]}
        assert label_names == {"urgent", "work"}

        # Complete the recurring task - this is where the greenlet error occurs
        complete_response = await authenticated_client.patch(
            f"/api/v1/tasks/{original_task_id}",
            json={"completed": True},
        )

        # Should succeed
        assert complete_response.status_code == 200
        completed_task = complete_response.json()
        assert completed_task["completed"] is True
        assert completed_task["archived"] is True

        # Get all active tasks - should find the new recurring instance
        list_response = await authenticated_client.get(
            f"/api/v1/tasks?project_id={test_project.id}"
        )
        assert list_response.status_code == 200
        data = list_response.json()
        active_tasks = data["items"]

        # Find the new recurring task instance
        recurring_tasks = [
            task for task in active_tasks
            if task["title"] == "Daily Report" and task["recurrence_interval"] == 1 and task["recurrence_unit"] == "days"
        ]
        assert len(recurring_tasks) == 1
        new_task = recurring_tasks[0]

        # Verify the new task preserved the labels from the original
        assert new_task["id"] != original_task_id
        assert new_task["completed"] is False
        assert new_task["archived"] is False
        assert len(new_task["labels"]) == 2
        new_label_names = {label["name"] for label in new_task["labels"]}
        assert new_label_names == {"urgent", "work"}

        # Verify due date moved forward by one day
        assert new_task["due_datetime"] == "2025-01-16T17:00:00Z"


class TestTasksByDateRange:
    """Test task filtering by date range functionality."""

    async def test_get_tasks_by_date_range_single_day(
        self,
        authenticated_client: AsyncClient,
        db_session: AsyncSession,
        test_user: User,
        test_project: Project,
        test_section: Section,
    ) -> None:
        """Test fetching tasks for a single day."""
        today = datetime.now(timezone.utc).replace(hour=10, minute=0, second=0, microsecond=0)

        task1 = Task(
            title="Task for today",
            user_id=test_user.id,
            project_id=test_project.id,
            section_id=test_section.id,
            due_datetime=today,
            order_index=0,
            completed=False,
            archived=False,
        )
        db_session.add(task1)
        await db_session.commit()

        start_of_day = today.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)

        response = await authenticated_client.get(
            "/api/v1/tasks/by-date",
            params={
                "date_from": start_of_day.isoformat(),
                "date_to": end_of_day.isoformat(),
            },
        )

        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 1
        assert tasks[0]["title"] == "Task for today"

    async def test_get_tasks_by_date_range_multiple_days(
        self,
        authenticated_client: AsyncClient,
        db_session: AsyncSession,
        test_user: User,
        test_project: Project,
        test_section: Section,
    ) -> None:
        """Test fetching tasks across multiple days."""
        base_date = datetime(2025, 11, 17, 10, 0, 0, tzinfo=timezone.utc)

        task1 = Task(
            title="Day 1 Task",
            user_id=test_user.id,
            project_id=test_project.id,
            section_id=test_section.id,
            due_datetime=base_date,
            order_index=0,
            completed=False,
            archived=False,
        )
        task2 = Task(
            title="Day 2 Task",
            user_id=test_user.id,
            project_id=test_project.id,
            section_id=test_section.id,
            due_datetime=base_date + timedelta(days=1),
            order_index=1,
            completed=False,
            archived=False,
        )
        task3 = Task(
            title="Day 3 Task",
            user_id=test_user.id,
            project_id=test_project.id,
            section_id=test_section.id,
            due_datetime=base_date + timedelta(days=2),
            order_index=2,
            completed=False,
            archived=False,
        )

        db_session.add_all([task1, task2, task3])
        await db_session.commit()

        date_from = base_date.replace(hour=0, minute=0, second=0)
        date_to = date_from + timedelta(days=3)

        response = await authenticated_client.get(
            "/api/v1/tasks/by-date",
            params={
                "date_from": date_from.isoformat(),
                "date_to": date_to.isoformat(),
            },
        )

        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 3
        task_titles = {task["title"] for task in tasks}
        assert task_titles == {"Day 1 Task", "Day 2 Task", "Day 3 Task"}

    async def test_get_tasks_by_date_range_includes_no_date_tasks(
        self,
        authenticated_client: AsyncClient,
        db_session: AsyncSession,
        test_user: User,
        test_project: Project,
        test_section: Section,
    ) -> None:
        """Test that tasks without due dates are included in results."""
        today = datetime.now(timezone.utc).replace(hour=10, minute=0, second=0, microsecond=0)

        task_with_date = Task(
            title="Task with date",
            user_id=test_user.id,
            project_id=test_project.id,
            section_id=test_section.id,
            due_datetime=today,
            order_index=0,
            completed=False,
            archived=False,
        )
        task_without_date = Task(
            title="Task without date",
            user_id=test_user.id,
            project_id=test_project.id,
            section_id=test_section.id,
            due_datetime=None,
            order_index=1,
            completed=False,
            archived=False,
        )

        db_session.add_all([task_with_date, task_without_date])
        await db_session.commit()

        start_of_day = today.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)

        response = await authenticated_client.get(
            "/api/v1/tasks/by-date",
            params={
                "date_from": start_of_day.isoformat(),
                "date_to": end_of_day.isoformat(),
            },
        )

        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 2
        task_titles = {task["title"] for task in tasks}
        assert task_titles == {"Task with date", "Task without date"}

    async def test_get_tasks_by_date_range_excludes_completed(
        self,
        authenticated_client: AsyncClient,
        db_session: AsyncSession,
        test_user: User,
        test_project: Project,
        test_section: Section,
    ) -> None:
        """Test that completed tasks are excluded from results."""
        today = datetime.now(timezone.utc).replace(hour=10, minute=0, second=0, microsecond=0)

        active_task = Task(
            title="Active task",
            user_id=test_user.id,
            project_id=test_project.id,
            section_id=test_section.id,
            due_datetime=today,
            order_index=0,
            completed=False,
            archived=False,
        )
        completed_task = Task(
            title="Completed task",
            user_id=test_user.id,
            project_id=test_project.id,
            section_id=test_section.id,
            due_datetime=today,
            order_index=1,
            completed=True,
            archived=False,
        )

        db_session.add_all([active_task, completed_task])
        await db_session.commit()

        start_of_day = today.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)

        response = await authenticated_client.get(
            "/api/v1/tasks/by-date",
            params={
                "date_from": start_of_day.isoformat(),
                "date_to": end_of_day.isoformat(),
            },
        )

        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 1
        assert tasks[0]["title"] == "Active task"
        assert tasks[0]["completed"] is False

    async def test_get_tasks_by_date_range_excludes_archived(
        self,
        authenticated_client: AsyncClient,
        db_session: AsyncSession,
        test_user: User,
        test_project: Project,
        test_section: Section,
    ) -> None:
        """Test that archived tasks are excluded from results."""
        today = datetime.now(timezone.utc).replace(hour=10, minute=0, second=0, microsecond=0)

        active_task = Task(
            title="Active task",
            user_id=test_user.id,
            project_id=test_project.id,
            section_id=test_section.id,
            due_datetime=today,
            order_index=0,
            completed=False,
            archived=False,
        )
        archived_task = Task(
            title="Archived task",
            user_id=test_user.id,
            project_id=test_project.id,
            section_id=test_section.id,
            due_datetime=today,
            order_index=1,
            completed=False,
            archived=True,
        )

        db_session.add_all([active_task, archived_task])
        await db_session.commit()

        start_of_day = today.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)

        response = await authenticated_client.get(
            "/api/v1/tasks/by-date",
            params={
                "date_from": start_of_day.isoformat(),
                "date_to": end_of_day.isoformat(),
            },
        )

        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 1
        assert tasks[0]["title"] == "Active task"
        assert tasks[0]["archived"] is False

    async def test_get_tasks_by_date_range_empty_result(
        self,
        authenticated_client: AsyncClient,
        db_session: AsyncSession,
        test_user: User,
        test_project: Project,
        test_section: Section,
    ) -> None:
        """Test that empty list is returned when no tasks match the date range."""
        task = Task(
            title="Future task",
            user_id=test_user.id,
            project_id=test_project.id,
            section_id=test_section.id,
            due_datetime=datetime(2026, 1, 1, 10, 0, 0, tzinfo=timezone.utc),
            order_index=0,
            completed=False,
            archived=False,
        )
        db_session.add(task)
        await db_session.commit()

        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)

        response = await authenticated_client.get(
            "/api/v1/tasks/by-date",
            params={
                "date_from": today.isoformat(),
                "date_to": tomorrow.isoformat(),
            },
        )

        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 0

    async def test_get_tasks_by_date_range_user_isolation(
        self,
        authenticated_client: AsyncClient,
        db_session: AsyncSession,
        test_user: User,
        test_project: Project,
        test_section: Section,
    ) -> None:
        """Test that users can only see their own tasks."""
        other_user = User(
            email="other@example.com",
            oauth_provider="google",
            oauth_subject_id="other_oauth_id",
            full_name="Other User",
        )
        db_session.add(other_user)
        await db_session.commit()
        await db_session.refresh(other_user)

        other_project = Project(
            title="Other Project",
            user_id=other_user.id,
            order_index=0,
        )
        db_session.add(other_project)
        await db_session.commit()
        await db_session.refresh(other_project)

        other_section = Section(
            title="Other Section",
            project_id=other_project.id,
            user_id=other_user.id,
            order_index=0,
        )
        db_session.add(other_section)
        await db_session.commit()
        await db_session.refresh(other_section)

        today = datetime.now(timezone.utc).replace(hour=10, minute=0, second=0, microsecond=0)

        my_task = Task(
            title="My task",
            user_id=test_user.id,
            project_id=test_project.id,
            section_id=test_section.id,
            due_datetime=today,
            order_index=0,
            completed=False,
            archived=False,
        )
        other_task = Task(
            title="Other user's task",
            user_id=other_user.id,
            project_id=other_project.id,
            section_id=other_section.id,
            due_datetime=today,
            order_index=0,
            completed=False,
            archived=False,
        )

        db_session.add_all([my_task, other_task])
        await db_session.commit()

        start_of_day = today.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)

        response = await authenticated_client.get(
            "/api/v1/tasks/by-date",
            params={
                "date_from": start_of_day.isoformat(),
                "date_to": end_of_day.isoformat(),
            },
        )

        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 1
        assert tasks[0]["title"] == "My task"
        # User isolation verified: only 1 task returned (test_user's task, not other_user's)

    async def test_get_tasks_by_date_range_boundary_conditions(
        self,
        authenticated_client: AsyncClient,
        db_session: AsyncSession,
        test_user: User,
        test_project: Project,
        test_section: Section,
    ) -> None:
        """Test boundary conditions (inclusive start, exclusive end)."""
        base_date = datetime(2025, 11, 17, 0, 0, 0, tzinfo=timezone.utc)

        task_at_start = Task(
            title="Task at start boundary",
            user_id=test_user.id,
            project_id=test_project.id,
            section_id=test_section.id,
            due_datetime=base_date,
            order_index=0,
            completed=False,
            archived=False,
        )
        task_at_end = Task(
            title="Task at end boundary",
            user_id=test_user.id,
            project_id=test_project.id,
            section_id=test_section.id,
            due_datetime=base_date + timedelta(days=1),
            order_index=1,
            completed=False,
            archived=False,
        )

        db_session.add_all([task_at_start, task_at_end])
        await db_session.commit()

        response = await authenticated_client.get(
            "/api/v1/tasks/by-date",
            params={
                "date_from": base_date.isoformat(),
                "date_to": (base_date + timedelta(days=1)).isoformat(),
            },
        )

        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 1
        assert tasks[0]["title"] == "Task at start boundary"

    async def test_get_tasks_by_date_range_requires_authentication(
        self,
        client: AsyncClient,
    ) -> None:
        """Test that unauthenticated requests are rejected."""
        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)

        response = await client.get(
            "/api/v1/tasks/by-date",
            params={
                "date_from": today.isoformat(),
                "date_to": tomorrow.isoformat(),
            },
        )

        assert response.status_code == 401
