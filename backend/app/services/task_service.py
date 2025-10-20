from collections.abc import Sequence
from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select, update

from app.models.task import Task
from app.schemas.task import TaskReorder
from app.services import streak_service


async def create_task(
    db: AsyncSession,
    user_id: UUID,
    title: str,
    description: str | None,
    project_id: UUID,
    section_id: UUID
) -> Task:
    """Create a new task for a user."""
    # Get the max order_index for this section to append new task at the end
    result = await db.execute(
        select(Task.order_index)
        .where(Task.section_id == section_id, Task.user_id == user_id)
        .order_by(Task.order_index.desc())
        .limit(1)
    )
    max_order = result.scalar()
    next_order_index = (max_order + 1) if max_order is not None else 0

    new_task = Task(
        user_id=user_id,
        title=title,
        description=description,
        project_id=project_id,
        section_id=section_id,
        completed=False,
        archived=False,
        order_index=next_order_index
    )
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    return new_task


async def get_task_by_id(db: AsyncSession, task_id: UUID, user_id: UUID) -> Task | None:
    """Retrieve a task by its ID and user ID."""
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    )
    return result.scalars().first()


async def get_tasks(db: AsyncSession, user_id: UUID) -> Sequence[Task]:
    """Retrieve all tasks for a specific user."""
    result = await db.execute(
        select(Task).where(Task.user_id == user_id, Task.archived == False)  # noqa: E712
        .order_by(Task.order_index)
    )
    return result.scalars().all()


async def get_tasks_by_project(
    db: AsyncSession,
    user_id: UUID,
    project_id: UUID,
) -> Sequence[Task]:
    """Retrieve all tasks for a specific project and user."""
    result = await db.execute(
        select(Task)
        .where(
            Task.user_id == user_id,
            Task.project_id == project_id,
            Task.archived == False  # noqa: E712
        )
        .order_by(Task.order_index)
    )
    return result.scalars().all()


async def get_archived_tasks(
    db: AsyncSession,
    user_id: UUID
) -> Sequence[Task]:
    """Retrieve all archived tasks for a specific user."""
    result = await db.execute(
        select(Task)
        .where(
            Task.user_id == user_id,
            Task.archived == True  # noqa: E712
        )
        .order_by(Task.order_index)
    )
    return result.scalars().all()


async def update_task(
    db: AsyncSession,
    task_id: UUID,
    user_id: UUID,
    title: str | None = None,
    description: str | None = None,
    completed: bool | None = None
) -> Task:
    """Update an existing task."""
    task = await get_task_by_id(db, task_id, user_id)
    if task is None:
        raise ValueError("Task not found")

    # Track if task is being marked complete for the first time
    was_incomplete = not task.completed
    is_now_complete = completed is True

    if title is not None:
        task.title = title
    if description is not None:
        task.description = description
    if completed is not None:
        task.completed = completed
        # Set completed_at timestamp when marking as complete
        if completed and was_incomplete:
            task.completed_at = datetime.now()

    db.add(task)
    await db.commit()
    await db.refresh(task)

    # Update streak if task was just completed
    if was_incomplete and is_now_complete:
        _ = await streak_service.update_streak_on_completion(db, user_id)

    return task


async def delete_task(db: AsyncSession, task_id: UUID, user_id: UUID) -> None:
    """Delete a task."""
    task = await get_task_by_id(db, task_id, user_id)
    if task is None:
        raise ValueError("Task not found")

    await db.delete(task)
    await db.commit()


async def reorder_tasks(db: AsyncSession, user_id: UUID, tasks_reorder: list[TaskReorder]) -> None:
    """Reorder tasks based on the provided list of task data."""
    task_ids = [t.id for t in tasks_reorder]

    result = await db.execute(
        select(Task).where(
            Task.id.in_(task_ids),
            Task.user_id == user_id
        )
    )
    tasks = {t.id: t for t in result.scalars().all()}

    if len(tasks) != len(task_ids):
        raise ValueError("One or more tasks not found")

    for task_data in tasks_reorder:
        task = tasks[task_data.id]
        task.order_index = task_data.order_index
        db.add(task)

    await db.commit()


async def archive_task(
    db: AsyncSession,
    task_id: UUID,
    user_id: UUID
) -> None:
    """Archive a specific task."""
    task = await get_task_by_id(db, task_id, user_id)
    if task is None:
        raise ValueError("Task not found")

    task.archived = True
    task.archived_at = datetime.now()
    db.add(task)
    await db.commit()


# app/services/task_service.py
async def archive_completed_tasks(
    db: AsyncSession,
    days: int = 7
) -> int:
    """Archive all completed tasks older than N days."""
    cutoff = datetime.now() - timedelta(days=days)

    result = await db.execute(
        update(Task)
        .where(
            Task.completed == True,  # noqa: E712
            Task.completed_at < cutoff,
            Task.archived == False  # noqa: E712
        )
        .values(archived=True, archived_at=datetime.now())
    )
    await db.commit()
    return result.rowcount  # Number of tasks archived
