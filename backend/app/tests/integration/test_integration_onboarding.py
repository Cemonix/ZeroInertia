"""
Integration tests for user onboarding features.

Tests cover:
- Tutorial project creation on first login
- Onboarding content structure and validation
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.models.section import Section
from app.models.task import Task
from app.models.user import User
from app.schemas.user import UserUpdate
from app.services.user_service import UserService

# pyright: reportAny=false


class TestTutorialCreation:
    """Test tutorial project creation on first login."""

    async def test_tutorial_created_on_first_login(self, db_session: AsyncSession) -> None:
        """Test that tutorial project is created when user logs in for the first time."""
        user = User(
            email="newuser@example.com",
            oauth_provider="google",
            oauth_subject_id="new_user_oauth_id",
            full_name="New User",
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        assert user.last_login_at is None

        update_data = UserUpdate()
        _ = await UserService.update_user(db_session, user, update_data)

        await db_session.refresh(user)
        assert user.last_login_at is not None

        result = await db_session.execute(
            select(Project).where(
                Project.user_id == user.id,
                Project.title == "🎓 Getting Started with Zero Inertia"
            )
        )
        tutorial_project = result.scalar_one_or_none()

        assert tutorial_project is not None
        assert tutorial_project.order_index == 0
        assert tutorial_project.is_inbox is False

    async def test_tutorial_not_created_on_second_login(self, db_session: AsyncSession) -> None:
        """Test that tutorial project is NOT created on subsequent logins."""
        user = User(
            email="existinguser@example.com",
            oauth_provider="google",
            oauth_subject_id="existing_user_oauth_id",
            full_name="Existing User",
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        update_data = UserUpdate()
        _ = await UserService.update_user(db_session, user, update_data)

        result = await db_session.execute(
            select(Project).where(
                Project.user_id == user.id,
                Project.title == "🎓 Getting Started with Zero Inertia"
            )
        )
        projects_after_first_login = result.scalars().all()
        tutorial_count_first = len(projects_after_first_login)

        assert tutorial_count_first == 1

        _ = await UserService.update_user(db_session, user, update_data)

        result = await db_session.execute(
            select(Project).where(
                Project.user_id == user.id,
                Project.title == "🎓 Getting Started with Zero Inertia"
            )
        )
        projects_after_second_login = result.scalars().all()
        tutorial_count_second = len(projects_after_second_login)

        assert tutorial_count_second == 1

    async def test_tutorial_has_correct_structure(self, db_session: AsyncSession) -> None:
        """Test that tutorial project has the expected sections and tasks."""
        user = User(
            email="tutorialtest@example.com",
            oauth_provider="google",
            oauth_subject_id="tutorial_test_oauth_id",
            full_name="Tutorial Test User",
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        update_data = UserUpdate()
        _ = await UserService.update_user(db_session, user, update_data)

        result = await db_session.execute(
            select(Project).where(
                Project.user_id == user.id,
                Project.title == "🎓 Getting Started with Zero Inertia"
            )
        )
        tutorial_project = result.scalar_one_or_none()
        assert tutorial_project is not None

        result = await db_session.execute(
            select(Section).where(Section.project_id == tutorial_project.id)
        )
        sections = result.scalars().all()
        assert len(sections) == 3

        section_titles = {section.title for section in sections}
        assert "The Basics" in section_titles
        assert "Projects & Organization" in section_titles
        assert "Advanced Features" in section_titles

        result = await db_session.execute(
            select(Task).where(Task.project_id == tutorial_project.id)
        )
        tasks = result.scalars().all()
        assert len(tasks) == 12

        assert any("Welcome to Zero Inertia" in task.title for task in tasks)
        assert any("due date" in task.title.lower() for task in tasks)
        assert any("priority" in task.title.lower() for task in tasks)
        assert any("description" in task.title.lower() for task in tasks)

        for task in tasks:
            assert task.completed is False
            assert task.archived is False
            assert task.description is not None and len(task.description) > 0
