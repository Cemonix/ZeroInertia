"""
Database-level integration tests.

These tests verify database operations, relationships,
and constraints work correctly.
"""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.models.project import Project
from app.models.section import Section
from app.models.task import Task
from app.models.user import User


class TestDatabaseOperations:
    """Test database operations and constraints."""

    async def test_task_completion_timestamp(
        self, db_session: AsyncSession, test_user: User
    ) -> None:
        """Test that task completion sets timestamp correctly."""
        # Create project and section first
        project = Project(
            title="Test Project", user_id=test_user.id, order_index=0
        )
        db_session.add(project)
        await db_session.commit()
        await db_session.refresh(project)

        from app.models.section import Section
        section = Section(
            title="Test Section",
            project_id=project.id,
            user_id=test_user.id,
            order_index=0,
        )
        db_session.add(section)
        await db_session.commit()
        await db_session.refresh(section)

        task = Task(
            title="Test Task",
            user_id=test_user.id,
            project_id=project.id,
            section_id=section.id,
            order_index=0,
            completed=False,
            archived=False,
        )
        db_session.add(task)
        await db_session.commit()
        await db_session.refresh(task)

        assert task.completed is False
        assert task.completed_at is None

        # Complete the task
        task.completed = True
        task.completed_at = datetime.now(timezone.utc)
        await db_session.commit()
        await db_session.refresh(task)

        assert task.completed is True
        assert task.completed_at is not None
        assert isinstance(task.completed_at, datetime)

    async def test_cascade_delete_project(
        self, db_session: AsyncSession, test_user: User
    ) -> None:
        """Test that deleting a project cascades to sections and tasks."""
        # Create project with tasks
        project = Project(
            title="Delete Me", user_id=test_user.id, order_index=0
        )
        db_session.add(project)
        await db_session.commit()
        await db_session.refresh(project)

        section = Section(
            title="Test Section",
            project_id=project.id,
            user_id=test_user.id,
            order_index=0,
        )
        db_session.add(section)
        await db_session.commit()
        await db_session.refresh(section)

        task = Task(
            title="Task",
            user_id=test_user.id,
            project_id=project.id,
            section_id=section.id,
            order_index=0,
            completed=False,
            archived=False,
        )
        db_session.add(task)
        await db_session.commit()
        task_id = task.id
        section_id = section.id

        # Delete project
        await db_session.delete(project)
        await db_session.commit()

        # Verify cascade: sections and tasks should be deleted
        result = await db_session.execute(
            select(Task).where(Task.id == task_id)
        )
        task_after_delete = result.scalar_one_or_none()
        assert task_after_delete is None, "Task should be cascade deleted with project"

        section_result = await db_session.execute(
            select(Section).where(Section.id == section_id)
        )
        section_after_delete = section_result.scalar_one_or_none()
        assert section_after_delete is None, "Section should be cascade deleted with project"

    async def test_unique_email_constraint(self, db_session: AsyncSession) -> None:
        """Test that email uniqueness is enforced."""
        from sqlalchemy.exc import IntegrityError

        # Create first user
        user1 = User(
            email="unique@example.com",
            oauth_provider="google",
            oauth_subject_id="unique_id_1",
        )
        db_session.add(user1)
        await db_session.commit()

        # Try to create second user with same email
        user2 = User(
            email="unique@example.com",
            oauth_provider="google",
            oauth_subject_id="unique_id_2",
        )
        db_session.add(user2)

        # Should raise integrity error
        try:
            await db_session.commit()
            raise AssertionError("Expected IntegrityError but commit succeeded")
        except IntegrityError:
            await db_session.rollback()
            # Expected behavior

    async def test_task_ordering_within_project(
        self, db_session: AsyncSession, test_user: User
    ) -> None:
        """Test that tasks maintain order within a project."""
        project = Project(
            title="Ordered Project", user_id=test_user.id, order_index=0
        )
        db_session.add(project)
        await db_session.commit()
        await db_session.refresh(project)

        section = Section(
            title="Test Section",
            project_id=project.id,
            user_id=test_user.id,
            order_index=0,
        )
        db_session.add(section)
        await db_session.commit()
        await db_session.refresh(section)

        # Create tasks with specific order
        tasks: list[Task] = []
        for i in range(5):
            task = Task(
                title=f"Task {i}",
                user_id=test_user.id,
                project_id=project.id,
                section_id=section.id,
                order_index=i,
                completed=False,
                archived=False,
            )
            tasks.append(task)
            db_session.add(task)

        await db_session.commit()

        # Query tasks ordered by order_index
        result = await db_session.execute(
            select(Task)
            .where(Task.project_id == project.id)
            .order_by(Task.order_index)
        )
        retrieved_tasks = result.scalars().all()

        assert len(retrieved_tasks) == 5
        for i, task in enumerate(retrieved_tasks):
            assert task.order_index == i
            assert task.title == f"Task {i}"

    async def test_filter_archived_tasks(
        self, db_session: AsyncSession, test_user: User
    ) -> None:
        """Test filtering archived vs active tasks."""
        # Create project and section first
        project = Project(
            title="Test Project", user_id=test_user.id, order_index=0
        )
        db_session.add(project)
        await db_session.commit()
        await db_session.refresh(project)

        section = Section(
            title="Test Section",
            project_id=project.id,
            user_id=test_user.id,
            order_index=0,
        )
        db_session.add(section)
        await db_session.commit()
        await db_session.refresh(section)

        # Create mix of archived and active tasks
        active_task = Task(
            title="Active",
            user_id=test_user.id,
            project_id=project.id,
            section_id=section.id,
            order_index=0,
            completed=False,
            archived=False,
        )
        archived_task = Task(
            title="Archived",
            user_id=test_user.id,
            project_id=project.id,
            section_id=section.id,
            order_index=1,
            completed=True,
            archived=True,
        )

        db_session.add_all([active_task, archived_task])
        await db_session.commit()

        # Query active tasks only
        result = await db_session.execute(
            select(Task).where(Task.user_id == test_user.id, Task.archived.is_(False))
        )
        active_tasks = result.scalars().all()

        assert len(active_tasks) == 1
        assert active_tasks[0].title == "Active"

        # Query archived tasks only
        result = await db_session.execute(
            select(Task).where(Task.user_id == test_user.id, Task.archived.is_(True))
        )
        archived_tasks = result.scalars().all()

        assert len(archived_tasks) == 1
        assert archived_tasks[0].title == "Archived"
