from collections.abc import Sequence
from datetime import datetime, timedelta, timezone
from typing import Any, cast
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import select, update

from app.models.label import Label
from app.models.task import Task
from app.schemas.task import TaskReorder
from app.services import streak_service


async def _get_labels_for_user(
    db: AsyncSession,
    user_id: UUID,
    label_ids: list[UUID] | None,
) -> Sequence[Label]:
    """Fetch labels by id enforcing user ownership."""
    if not label_ids:
        return []

    unique_label_ids = set(label_ids)
    result = await db.execute(
        select(Label).where(Label.id.in_(unique_label_ids), Label.user_id == user_id)
    )
    labels = result.scalars().all()
    if len(labels) != len(unique_label_ids):
        raise ValueError("One or more labels not found")
    return labels


async def create_task(
    db: AsyncSession,
    user_id: UUID,
    title: str,
    description: str | None,
    project_id: UUID,
    section_id: UUID,
    priority_id: UUID | None = None,
    due_datetime: datetime | None = None,
    label_ids: list[UUID] | None = None,
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
        order_index=next_order_index,
        priority_id=priority_id,
        due_datetime=due_datetime
    )

    db.add(new_task)

    if label_ids is not None:
        labels = await _get_labels_for_user(db=db, user_id=user_id, label_ids=label_ids)
        new_task.labels = list(labels)

    try:
        await db.commit()
    except IntegrityError as e:
        await db.rollback()
        # Parse the error to provide helpful feedback
        error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
        if 'section_id' in error_msg:
            raise ValueError("Section not found or does not belong to you") from e
        elif 'project_id' in error_msg:
            raise ValueError("Project not found or does not belong to you") from e
        elif 'priority_id' in error_msg:
            raise ValueError("Priority not found") from e
        else:
            raise ValueError("Invalid reference: one or more related entities not found") from e

    await db.refresh(new_task)
    return new_task


async def get_task_by_id(db: AsyncSession, task_id: UUID, user_id: UUID) -> Task | None:
    """Retrieve a task by its ID and user ID."""
    result = await db.execute(
        select(Task)
        .options(selectinload(Task.labels))  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
        .where(Task.id == task_id, Task.user_id == user_id)
    )
    return result.scalars().first()


async def get_tasks(db: AsyncSession, user_id: UUID) -> Sequence[Task]:
    """Retrieve all tasks for a specific user."""
    result = await db.execute(
        select(Task)
        .options(selectinload(Task.labels))  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
        .where(Task.user_id == user_id, Task.archived == False)  # noqa: E712
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
        .options(selectinload(Task.labels))  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
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
        .options(selectinload(Task.labels))  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
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
    **updates: dict[str, Any],  # pyright: ignore[reportExplicitAny]
) -> Task:
    """
    Update an existing task.

    Only fields provided in updates dict will be modified.
    Passing None for a field will set it to NULL (e.g., clearing due_datetime).
    """
    task = await get_task_by_id(db, task_id, user_id)
    if task is None:
        raise ValueError("Task not found")

    # Track if task is being marked complete for the first time
    was_incomplete = not task.completed
    completed_value = cast(bool | None, updates.get("completed"))
    is_now_complete = completed_value is True

    # Update only the fields that were provided
    if "title" in updates:
        task.title = updates["title"]  # pyright: ignore[reportAttributeAccessIssue]
    if "description" in updates:
        task.description = updates["description"]  # pyright: ignore[reportAttributeAccessIssue]
    if "completed" in updates:
        task.completed = updates["completed"]  # pyright: ignore[reportAttributeAccessIssue]
        # Set completed_at timestamp when marking as complete
        if completed_value and was_incomplete:
            task.completed_at = datetime.now(timezone.utc)
    if "priority_id" in updates:
        task.priority_id = updates["priority_id"]  # pyright: ignore[reportAttributeAccessIssue]
    if "due_datetime" in updates:
        task.due_datetime = updates["due_datetime"]  # pyright: ignore[reportAttributeAccessIssue]
    if "label_ids" in updates:
        label_ids = updates["label_ids"]
        if label_ids is not None:  # pyright: ignore[reportUnnecessaryComparison]
            labels = await _get_labels_for_user(db=db, user_id=user_id, label_ids=label_ids)  # pyright: ignore[reportArgumentType]
            task.labels = list(labels)
        else:
            task.labels = []

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
    task.archived_at = datetime.now(timezone.utc)
    db.add(task)
    await db.commit()


# app/services/task_service.py
async def archive_completed_tasks(
    db: AsyncSession,
    days: int = 7
) -> int:
    """Archive all completed tasks older than N days."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    result = await db.execute(
        update(Task)
        .where(
            Task.completed == True,  # noqa: E712
            Task.completed_at < cutoff,
            Task.archived == False  # noqa: E712
        )
        .values(archived=True, archived_at=datetime.now(timezone.utc))
    )
    await db.commit()
    return result.rowcount  # Number of tasks archived
