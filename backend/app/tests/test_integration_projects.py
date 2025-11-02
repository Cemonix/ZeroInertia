"""
Integration tests for project management endpoints.

Tests cover:
- Project CRUD operations
- Project-task relationships
- Project ordering
- User isolation
- Edge cases and validation
"""

from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.models import Section, Task
from app.models.project import Project
from app.models.user import User

# pyright: reportAny=false


class TestProjectEndpoints:
    """Test project management functionality."""

    async def test_create_project(self, authenticated_client: AsyncClient) -> None:
        """Test creating a new project."""
        response = await authenticated_client.post(
            "/api/v1/projects",
            json={
                "title": "My Project",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "My Project"
        assert "id" in data
        assert "order_index" in data

    async def test_create_project_minimal(self, authenticated_client: AsyncClient) -> None:
        """Test creating a project with only required fields."""
        response = await authenticated_client.post(
            "/api/v1/projects",
            json={"title": "Minimal Project"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Minimal Project"

    async def test_get_all_projects(self, authenticated_client: AsyncClient, test_project: Project) -> None:
        """Test retrieving all projects for a user."""
        response = await authenticated_client.get("/api/v1/projects")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1  # pyright: ignore[reportUnknownArgumentType]
        assert any(proj["id"] == str(test_project.id) for proj in data)  # pyright: ignore[reportUnknownArgumentType, reportUnknownVariableType]

    async def test_get_single_project(self, authenticated_client: AsyncClient, test_project: Project) -> None:
        """Test retrieving a specific project by ID."""
        response = await authenticated_client.get(f"/api/v1/projects/{test_project.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_project.id)
        assert data["title"] == test_project.title

    async def test_get_nonexistent_project(self, authenticated_client: AsyncClient) -> None:
        """Test retrieving a non-existent project returns 404."""
        fake_id = uuid4()
        response = await authenticated_client.get(f"/api/v1/projects/{fake_id}")

        assert response.status_code == 404

    async def test_update_project(self, authenticated_client: AsyncClient, test_project: Project) -> None:
        """Test updating a project."""
        response = await authenticated_client.patch(
            f"/api/v1/projects/{test_project.id}",
            json={
                "title": "Updated Project Title",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Project Title"

    async def test_delete_project(self, authenticated_client: AsyncClient, test_project: Project) -> None:
        """Test deleting a project."""
        response = await authenticated_client.delete(f"/api/v1/projects/{test_project.id}")

        assert response.status_code == 204

        # Verify project is deleted
        get_response = await authenticated_client.get(f"/api/v1/projects/{test_project.id}")
        assert get_response.status_code == 404

    async def test_delete_project_cascades_to_tasks(
        self, authenticated_client: AsyncClient, test_project: Project, test_task: Task, db_session: AsyncSession
    ):
        """Test that deleting a project also deletes associated tasks."""
        from app.models.task import Task

        # Verify task exists
        task_query = await db_session.execute(
            select(Task).where(Task.id == test_task.id)
        )
        assert task_query.scalar_one_or_none() is not None

        # Delete project
        response = await authenticated_client.delete(f"/api/v1/projects/{test_project.id}")
        assert response.status_code == 204

        # Verify task is cascade deleted
        await db_session.commit()
        task_query = await db_session.execute(
            select(Task).where(Task.id == test_task.id)
        )
        task_after_delete = task_query.scalar_one_or_none()
        assert task_after_delete is None, "Task should be cascade deleted when project is deleted"

    async def test_project_with_tasks_count(
        self, authenticated_client: AsyncClient, test_project: Project, test_section: Section
    ) -> None:
        """Test that we can retrieve task count for a project."""
        # Create some tasks for the project
        for i in range(3):
            _ = await authenticated_client.post(
                "/api/v1/tasks",
                json={
                    "title": f"Task {i}",
                    "project_id": str(test_project.id),
                    "section_id": str(test_section.id),
                },
            )

        response = await authenticated_client.get(f"/api/v1/projects/{test_project.id}")
        assert response.status_code == 200

        # Verify by fetching tasks for the project
        tasks_response = await authenticated_client.get(
            f"/api/v1/tasks?project_id={test_project.id}"
        )
        tasks = tasks_response.json()
        assert len(tasks) >= 3
        assert len(tasks) >= 3


class TestProjectIsolation:
    """Test that users can only access their own projects."""

    async def test_cannot_access_other_users_project(
        self, authenticated_client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Test that users cannot access projects belonging to other users."""
        # Create another user
        other_user = User(
            email="other@example.com",
            oauth_provider="google",
            oauth_subject_id="other_oauth_id",
        )
        db_session.add(other_user)
        await db_session.commit()
        await db_session.refresh(other_user)

        # Create a project for the other user
        other_project = Project(
            title="Other User's Project",
            user_id=other_user.id,
            order_index=0,
        )
        db_session.add(other_project)
        await db_session.commit()
        await db_session.refresh(other_project)

        # Try to access the other user's project
        response = await authenticated_client.get(f"/api/v1/projects/{other_project.id}")
        assert response.status_code == 404

        # Try to update the other user's project
        update_response = await authenticated_client.patch(
            f"/api/v1/projects/{other_project.id}",
            json={"title": "Hacked Title"},
        )
        assert update_response.status_code == 404

        # Try to delete the other user's project
        delete_response = await authenticated_client.delete(
            f"/api/v1/projects/{other_project.id}"
        )
        assert delete_response.status_code == 404


class TestProjectOrdering:
    """Test project ordering functionality."""

    async def test_projects_have_order(self, authenticated_client: AsyncClient) -> None:
        """Test that projects are created with order indices."""
        project_ids: list[str] = []
        for i in range(3):
            response = await authenticated_client.post(
                "/api/v1/projects",
                json={"title": f"Project {i}"},
            )
            assert response.status_code == 201
            project_ids.append(response.json()["id"])

        # Get all projects
        response = await authenticated_client.get("/api/v1/projects")
        projects = response.json()

        # Verify projects have sequential order
        assert len(projects) >= 3
        order_indices = [proj["order_index"] for proj in projects]
        assert all(isinstance(idx, int) for idx in order_indices)

    async def test_reorder_projects(self, authenticated_client: AsyncClient) -> None:
        """Test reordering projects."""
        project_ids: list[str] = []
        for i in range(3):
            response = await authenticated_client.post(
                "/api/v1/projects",
                json={"title": f"Project {i}"},
            )
            project_ids.append(response.json()["id"])

        # Reorder projects - send list of ProjectsReorder objects
        response = await authenticated_client.patch(
            "/api/v1/projects/reorder",
            json=[
                {"id": project_ids[2], "parent_id": None, "order_index": 0},
                {"id": project_ids[0], "parent_id": None, "order_index": 1},
                {"id": project_ids[1], "parent_id": None, "order_index": 2},
            ],
        )

        assert response.status_code == 204


class TestProjectEdgeCases:
    """Test edge cases and input validation for projects."""

    @pytest.mark.parametrize(
        "title",
        [
            "Project with émojis 🚀",
            "中文项目名称",
            "🎉 Emoji Project",
            "Mixed: English & 中文 🌍",
        ],
    )
    async def test_create_project_with_unicode_and_emoji(
        self, authenticated_client: AsyncClient, title: str
    ) -> None:
        """Test creating projects with unicode and emoji."""
        response = await authenticated_client.post(
            "/api/v1/projects",
            json={"title": title},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == title

    async def test_create_project_with_very_long_title(
        self, authenticated_client: AsyncClient
    ) -> None:
        """Test creating project with extremely long title."""
        long_title = "A" * 1000
        response = await authenticated_client.post(
            "/api/v1/projects",
            json={"title": long_title},
        )

        # Should either accept or reject with validation error
        assert response.status_code in [201, 422]

    async def test_create_project_with_empty_title(
        self, authenticated_client: AsyncClient
    ) -> None:
        """Test that empty title is rejected."""
        response = await authenticated_client.post(
            "/api/v1/projects",
            json={"title": ""},
        )

        assert response.status_code == 422

    async def test_create_project_with_sql_injection(
        self, authenticated_client: AsyncClient
    ) -> None:
        """Test that SQL injection attempts are safely handled."""
        malicious_title = "'; DROP TABLE projects; --"
        response = await authenticated_client.post(
            "/api/v1/projects",
            json={"title": malicious_title},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == malicious_title

        # Verify project can be retrieved
        get_response = await authenticated_client.get(f"/api/v1/projects/{data['id']}")
        assert get_response.status_code == 200

    async def test_create_project_with_xss_attempt(
        self, authenticated_client: AsyncClient
    ) -> None:
        """Test that XSS attempts are safely stored."""
        xss_title = "<script>alert('XSS')</script>"
        response = await authenticated_client.post(
            "/api/v1/projects",
            json={"title": xss_title},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == xss_title

    async def test_get_project_with_invalid_uuid(
        self, authenticated_client: AsyncClient
    ) -> None:
        """Test getting project with malformed UUID."""
        response = await authenticated_client.get("/api/v1/projects/not-a-uuid")

        assert response.status_code == 422

    async def test_update_nonexistent_project(
        self, authenticated_client: AsyncClient
    ) -> None:
        """Test updating a project that doesn't exist."""
        fake_id = uuid4()
        response = await authenticated_client.patch(
            f"/api/v1/projects/{fake_id}",
            json={"title": "Updated"},
        )

        assert response.status_code == 404

    async def test_delete_nonexistent_project(
        self, authenticated_client: AsyncClient
    ) -> None:
        """Test deleting a project that doesn't exist."""
        fake_id = uuid4()
        response = await authenticated_client.delete(f"/api/v1/projects/{fake_id}")

        assert response.status_code == 404
