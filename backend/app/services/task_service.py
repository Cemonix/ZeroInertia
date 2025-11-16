import calendar
from collections.abc import Sequence
from datetime import datetime, timedelta, timezone
from typing import cast
from uuid import UUID

from sqlalchemy import case, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import select, update

from app.core.exceptions import (
    InvalidOperationException,
    InvalidReferenceException,
    LabelNotFoundException,
    PriorityNotFoundException,
    ProjectNotFoundException,
    SectionNotFoundException,
    TaskNotFoundException,
)
from app.models.label import Label
from app.models.section import Section
from app.models.task import Task
from app.schemas.task import TaskReorder, TaskUpdate
from app.services import streak_service
from app.services.base_service import apply_updates_async
from app.services.project_service import get_inbox_project

# pyright: reportAttributeAccessIssue=false, reportUnknownMemberType=false, reportUnknownArgumentType=false

DEFAULT_SNOOZE_INTERVAL = timedelta(days=1)


async def create_task(
    db: AsyncSession,
    user_id: UUID,
    title: str,
    description: str | None,
    project_id: UUID | None,
    section_id: UUID | None,
    priority_id: UUID | None = None,
    due_datetime: datetime | None = None,
    recurrence_interval: int | None = None,
    recurrence_unit: str | None = None,
    recurrence_days: list[int] | None = None,
    label_ids: list[UUID] | None = None,
    reminder_minutes: int | None = None,
    duration_minutes: int | None = None,
) -> Task:
    """Create a new task for a user."""
    # If no project_id provided, assign to inbox
    if project_id is None:
        inbox_project = await get_inbox_project(db, user_id)
        if inbox_project is None:
            raise InvalidOperationException("Inbox project not found for user")
        project_id = inbox_project.id

        # Get the default section of the inbox project
        if section_id is None:
            result = await db.execute(
                select(Section).where(
                    Section.project_id == project_id,
                    Section.user_id == user_id
                ).limit(1)
            )
            inbox_section = result.scalars().first()
            if inbox_section is None:
                raise InvalidOperationException("Inbox section not found")
            section_id = inbox_section.id

    # Ensure section_id is provided if project_id was provided
    if section_id is None:
        raise InvalidOperationException("section_id must be provided when project_id is specified")

    # Get the max order_index for this section to append new task at the end
    result = await db.execute(
        select(Task.order_index)
        .where(Task.section_id == section_id, Task.user_id == user_id)
        .order_by(Task.order_index.desc())
        .limit(1)
    )
    max_order = result.scalar()
    next_order_index = (max_order + 1) if max_order is not None else 0

    # Fetch labels before creating the task (if provided)
    labels = []
    if label_ids is not None:
        labels = await _get_labels_for_user(db=db, user_id=user_id, label_ids=label_ids)

    # Create task with all relationships set during construction
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
        due_datetime=due_datetime,
        recurrence_interval=recurrence_interval,
        recurrence_unit=recurrence_unit,
        recurrence_days=recurrence_days,
        reminder_minutes=reminder_minutes,
        duration_minutes=duration_minutes,
        labels=list(labels),  # Set labels during construction
    )

    db.add(new_task)

    try:
        await db.commit()
    except IntegrityError as e:
        await db.rollback()
        # Parse the error to provide helpful feedback
        error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
        if 'section_id' in error_msg:
            raise SectionNotFoundException() from e
        elif 'project_id' in error_msg:
            raise ProjectNotFoundException() from e
        elif 'priority_id' in error_msg:
            raise PriorityNotFoundException() from e
        else:
            raise InvalidReferenceException() from e

    await db.refresh(new_task)
    return new_task


async def get_task_by_id(db: AsyncSession, task_id: UUID, user_id: UUID) -> Task | None:
    """Retrieve a task by its ID and user ID."""
    result = await db.execute(
        select(Task)
        .options(selectinload(Task.labels))
        .where(Task.id == task_id, Task.user_id == user_id)
    )
    return result.scalars().first()


async def get_tasks(
    db: AsyncSession,
    user_id: UUID,
    skip: int = 0,
    limit: int = 50,
) -> tuple[Sequence[Task], int]:
    """
    Retrieve tasks for a specific user with pagination.

    Args:
        db: Database session
        user_id: User ID to filter tasks
        skip: Number of records to skip (offset)
        limit: Maximum number of records to return

    Returns:
        Tuple of (tasks, total_count)
    """
    # Count total tasks
    count_result = await db.execute(
        select(func.count(Task.id)).where(
            Task.user_id == user_id,
            Task.archived.is_(False),
        )
    )
    total = count_result.scalar_one()

    # Get paginated tasks
    result = await db.execute(
        select(Task)
        .options(selectinload(Task.labels))
        .where(Task.user_id == user_id, Task.archived.is_(False))
        .order_by(Task.order_index)
        .offset(skip)
        .limit(limit)
    )
    tasks = result.scalars().all()

    return tasks, total


async def get_tasks_by_date_range(
    db: AsyncSession,
    user_id: UUID,
    date_from: datetime,
    date_to: datetime,
) -> Sequence[Task]:
    """
    Retrieve tasks for a specific user within a date range.
    Includes tasks with due_datetime in range and tasks without a due date.

    Args:
        db: Database session
        user_id: User ID to filter tasks
        date_from: Start of date range (inclusive)
        date_to: End of date range (exclusive)

    Returns:
        List of tasks
    """
    result = await db.execute(
        select(Task)
        .options(selectinload(Task.labels))
        .where(
            Task.user_id == user_id,
            Task.archived.is_(False),
            Task.completed.is_(False),
            (
                (Task.due_datetime >= date_from) & (Task.due_datetime < date_to)
                | Task.due_datetime.is_(None)
            )
        )
        .order_by(Task.due_datetime.asc().nullslast(), Task.order_index)
    )
    tasks = result.scalars().all()
    return tasks


async def get_tasks_by_project(
    db: AsyncSession,
    user_id: UUID,
    project_id: UUID,
    skip: int = 0,
    limit: int = 50,
) -> tuple[Sequence[Task], int]:
    """
    Retrieve tasks for a specific project with pagination.

    Args:
        db: Database session
        user_id: User ID to filter tasks
        project_id: Project ID to filter tasks
        skip: Number of records to skip (offset)
        limit: Maximum number of records to return

    Returns:
        Tuple of (tasks, total_count)
    """
    # Count total tasks
    count_result = await db.execute(
        select(func.count(Task.id)).where(
            Task.user_id == user_id,
            Task.project_id == project_id,
            Task.archived.is_(False),
        )
    )
    total = count_result.scalar_one()

    # Get paginated tasks
    result = await db.execute(
        select(Task)
        .options(selectinload(Task.labels))
        .where(
            Task.user_id == user_id,
            Task.project_id == project_id,
            Task.archived.is_(False)
        )
        .order_by(Task.order_index)
        .offset(skip)
        .limit(limit)
    )
    tasks = result.scalars().all()

    return tasks, total


async def get_archived_tasks(
    db: AsyncSession,
    user_id: UUID,
    skip: int = 0,
    limit: int = 50,
) -> tuple[Sequence[Task], int]:
    """
    Retrieve archived tasks for a specific user with pagination.

    Args:
        db: Database session
        user_id: User ID to filter tasks
        skip: Number of records to skip (offset)
        limit: Maximum number of records to return

    Returns:
        Tuple of (tasks, total_count)
    """
    # Count total archived tasks
    count_result = await db.execute(
        select(func.count(Task.id)).where(
            Task.user_id == user_id,
            Task.archived.is_(True),
        )
    )
    total = count_result.scalar_one()

    # Get paginated archived tasks
    result = await db.execute(
        select(Task)
        .options(selectinload(Task.labels))
        .where(
            Task.user_id == user_id,
            Task.archived.is_(True)
        )
        .order_by(Task.order_index)
        .offset(skip)
        .limit(limit)
    )
    tasks = result.scalars().all()

    return tasks, total


async def get_active_task_counts_by_project(
    db: AsyncSession,
    user_id: UUID,
) -> dict[str, int]:
    """Return a mapping of project_id -> active task count for the given user.

    Active tasks are those that are not completed and not archived.
    """
    result = await db.execute(
        select(Task.project_id, func.count(Task.id))
        .where(
            Task.user_id == user_id,
            Task.completed.is_(False),
            Task.archived.is_(False),
        )
        .group_by(Task.project_id)
    )
    rows = result.all()
    return {str(project_id): count for project_id, count in rows}  # pyright: ignore[reportAny]


async def _handle_task_move(
    task: Task,
    user_id: UUID,
    db: AsyncSession,
    updates: dict[str, object],
) -> None:
    """Handle moving a task to a different project/section."""
    new_project_id = cast(UUID | None, updates.get("project_id", task.project_id))
    new_section_id = cast(UUID | None, updates.get("section_id", task.section_id))

    if new_project_id is None or new_section_id is None:
        raise InvalidOperationException("Both project_id and section_id are required to move a task")

    section_result = await db.execute(
        select(Section).where(
            Section.id == new_section_id,
            Section.user_id == user_id,
        )
    )
    section = section_result.scalars().first()
    if section is None or section.project_id != new_project_id:
        raise InvalidOperationException("Target section does not belong to the specified project")

    order_result = await db.execute(
        select(Task.order_index)
        .where(Task.section_id == new_section_id, Task.user_id == user_id)
        .order_by(Task.order_index.desc())
        .limit(1)
    )
    max_order = order_result.scalar()
    next_order_index = (max_order + 1) if max_order is not None else 0

    task.project_id = new_project_id
    task.section_id = new_section_id
    task.order_index = next_order_index


async def _handle_label_updates(
    task: Task,
    user_id: UUID,
    db: AsyncSession,
    label_ids: list[UUID] | None,
) -> None:
    """Handle updating task labels (many-to-many relationship)."""
    if label_ids is not None:
        labels = await _get_labels_for_user(db=db, user_id=user_id, label_ids=label_ids)
        task.labels.clear()
        task.labels.extend(labels)
    else:
        task.labels.clear()


async def _apply_task_updates(
    task: Task,
    user_id: UUID,
    db: AsyncSession,
    was_incomplete: bool,
    update_data: TaskUpdate,
) -> None:
    """Apply update fields to a task using Pydantic schema validation."""
    updates = update_data.model_dump(exclude_unset=True)
    completed_value = cast(bool | None, updates.get("completed"))

    # Handle project/section moves (including cross-project)
    if "project_id" in updates or "section_id" in updates:
        await _handle_task_move(task, user_id, db, updates)

    # Handle labels separately (many-to-many relationship)
    if "label_ids" in updates:
        await _handle_label_updates(task, user_id, db, updates["label_ids"])  # pyright: ignore[reportAny]

    # Handle completion timestamp
    if "completed" in updates and completed_value and was_incomplete:
        task.completed_at = datetime.now(timezone.utc)

    # Apply all other standard field updates
    _ = await apply_updates_async(
        model=task,
        update_schema=update_data,
        exclude_fields={"project_id", "section_id", "order_index", "label_ids"}
    )


async def _handle_recurring_task_completion(
    db: AsyncSession,
    task: Task,
    user_id: UUID,
) -> None:
    """Archive completed recurring task and create new instance for next occurrence."""
    # Save task info before archiving (we know recurrence_type is not None at this point)
    # Access labels while task is still in session to avoid greenlet errors
    task_labels = cast(Sequence[Label], task.labels)
    saved_label_ids = [label.id for label in task_labels] if task_labels else None

    saved_title = task.title
    saved_description = task.description
    saved_project_id = task.project_id
    saved_section_id = task.section_id
    saved_priority_id = task.priority_id
    saved_due_datetime = task.due_datetime
    saved_recurrence_interval = task.recurrence_interval
    saved_recurrence_unit = task.recurrence_unit
    saved_recurrence_days = task.recurrence_days
    saved_reminder_minutes = task.reminder_minutes
    saved_duration_minutes = task.duration_minutes

    # Archive the task and clear recurrence fields
    task.archived = True
    task.archived_at = datetime.now(timezone.utc)
    task.recurrence_interval = None
    task.recurrence_unit = None
    task.recurrence_days = None

    # Calculate next due date and create new task instance
    next_due_date = _calculate_next_due_date(
        saved_due_datetime,
        saved_recurrence_interval,
        saved_recurrence_unit,
        saved_recurrence_days
    )

    _ = await create_task(
        db=db,
        user_id=user_id,
        title=saved_title,
        description=saved_description,
        project_id=saved_project_id,
        section_id=saved_section_id,
        priority_id=saved_priority_id,
        due_datetime=next_due_date,
        recurrence_interval=saved_recurrence_interval,
        recurrence_unit=saved_recurrence_unit,
        recurrence_days=saved_recurrence_days,
        label_ids=saved_label_ids,
        reminder_minutes=saved_reminder_minutes,
        duration_minutes=saved_duration_minutes,
    )


async def update_task(
    db: AsyncSession,
    task_id: UUID,
    user_id: UUID,
    update_data: TaskUpdate,
) -> Task:
    """
    Update an existing task.

    Only fields provided in update_data will be modified.
    Passing None for a field will set it to NULL (e.g., clearing due_datetime).
    """
    task = await get_task_by_id(db, task_id, user_id)
    if task is None:
        raise TaskNotFoundException(str(task_id))

    # Track completion state for side effects
    was_incomplete = not task.completed
    updates = update_data.model_dump(exclude_unset=True)
    completed_value = cast(bool | None, updates.get("completed"))
    is_marking_complete = completed_value is True
    is_recurring = task.recurrence_interval is not None and task.recurrence_unit is not None
    is_completing_recurring_task = was_incomplete and is_marking_complete and is_recurring

    # Apply field updates
    await _apply_task_updates(task, user_id, db, was_incomplete, update_data)

    # Handle recurring task completion (archive + create new instance)
    if is_completing_recurring_task:
        await _handle_recurring_task_completion(db, task, user_id)

    # Commit all changes
    db.add(task)
    await db.commit()
    await db.refresh(task)

    # Update streak after successful completion
    if was_incomplete and is_marking_complete:
        _ = await streak_service.update_streak_on_completion(db, user_id)

    return task


async def delete_task(db: AsyncSession, task_id: UUID, user_id: UUID) -> None:
    """Delete a task."""
    task = await get_task_by_id(db, task_id, user_id)
    if task is None:
        raise TaskNotFoundException(str(task_id))

    await db.delete(task)
    await db.commit()


async def reorder_tasks(db: AsyncSession, user_id: UUID, tasks_reorder: list[TaskReorder]) -> None:
    """Reorder tasks based on the provided list of task data using bulk update."""
    # Early return if no tasks to reorder
    if not tasks_reorder:
        return

    task_ids = [t.id for t in tasks_reorder]

    # Verify all tasks exist and belong to the user
    result = await db.execute(
        select(Task.id).where(
            Task.id.in_(task_ids),
            Task.user_id == user_id
        )
    )
    existing_task_ids = set(result.scalars().all())

    if len(existing_task_ids) != len(task_ids):
        raise TaskNotFoundException()

    # Verify all target sections belong to their specified projects and to the user
    section_project_pairs = {(tr.section_id, tr.project_id) for tr in tasks_reorder}
    for section_id, project_id in section_project_pairs:
        section_result = await db.execute(
            select(Section).where(
                Section.id == section_id,
                Section.user_id == user_id,
            )
        )
        section = section_result.scalars().first()
        if section is None or section.project_id != project_id:
            raise InvalidOperationException("Target section does not belong to the specified project")

    # Perform a single set-based UPDATE using CASE expressions per column.
    # This avoids per-row ORM bulk update requirements and reserved bindparam names.
    order_map = {tr.id: tr.order_index for tr in tasks_reorder}
    section_map = {tr.id: tr.section_id for tr in tasks_reorder}
    project_map = {tr.id: tr.project_id for tr in tasks_reorder}

    # Build searched CASE expressions: CASE WHEN Task.id=<id> THEN <value> ... END
    order_whens = [(Task.id == tid, idx) for tid, idx in order_map.items()]
    section_whens = [(Task.id == tid, sid) for tid, sid in section_map.items()]
    project_whens = [(Task.id == tid, pid) for tid, pid in project_map.items()]

    order_case = case(*order_whens, else_=Task.order_index)
    section_case = case(*section_whens, else_=Task.section_id)
    project_case = case(*project_whens, else_=Task.project_id)

    stmt = (
        update(Task)
        .execution_options(synchronize_session=None)
        .where(Task.id.in_(task_ids), Task.user_id == user_id)
        .values(order_index=order_case, section_id=section_case, project_id=project_case)
    )

    _ = await db.execute(stmt)

    await db.commit()


async def archive_task(
    db: AsyncSession,
    task_id: UUID,
    user_id: UUID
) -> None:
    """Archive a specific task."""
    task = await get_task_by_id(db, task_id, user_id)
    if task is None:
        raise TaskNotFoundException(str(task_id))

    task.archived = True
    task.archived_at = datetime.now(timezone.utc)
    db.add(task)
    await db.commit()


async def snooze_task(
    db: AsyncSession,
    task_id: UUID,
    user_id: UUID,
    *,
    snooze_interval: timedelta = DEFAULT_SNOOZE_INTERVAL,
) -> Task:
    """Snooze a task by adjusting its due date and incrementing snooze count."""
    task = await get_task_by_id(db, task_id, user_id)
    if task is None:
        raise TaskNotFoundException(str(task_id))

    if task.due_datetime is None:
        raise InvalidOperationException("Task does not have a due date to snooze")

    now = datetime.now(timezone.utc)
    base_date = (
        task.due_datetime
        if task.due_datetime > now
        else task.due_datetime.combine(now.date(), task.due_datetime.time(), tzinfo=timezone.utc)
    )

    if task.recurrence_interval and task.recurrence_unit:
        next_due = _calculate_next_due_date(
            base_date,
            task.recurrence_interval,
            task.recurrence_unit,
            task.recurrence_days,
        )
    else:
        next_due = base_date + snooze_interval

    task.due_datetime = next_due
    task.snooze_count += 1

    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


async def archive_completed_tasks(
    db: AsyncSession,
    days: int = 7
) -> int:
    """Archive all completed tasks older than N days."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    result = await db.execute(
        update(Task)
        .where(
            Task.completed.is_(True),
            Task.completed_at < cutoff,
            Task.archived.is_(False)
        )
        .values(archived=True, archived_at=datetime.now(timezone.utc))
    )
    await db.commit()
    return result.rowcount  # Number of tasks archived


def _calculate_next_due_date(
    current_due: datetime | None,
    recurrence_interval: int | None,
    recurrence_unit: str | None,
    recurrence_days: list[int] | None
) -> datetime:
    """
    Calculate the next due date based on recurrence settings.

    Args:
        current_due: Current due date (uses now if None)
        recurrence_interval: Number of units between recurrences
        recurrence_unit: Unit type (days, weeks, months, years)
        recurrence_days: Specific weekdays for weekly recurrence (0=Mon, 6=Sun)

    Returns:
        Next due date as timezone-aware datetime
    """
    now = datetime.now(timezone.utc)
    base_date = current_due if current_due else now

    if recurrence_interval is None or recurrence_unit is None:
        return base_date + timedelta(days=1)

    if recurrence_unit == "days":
        return base_date + timedelta(days=recurrence_interval)

    elif recurrence_unit == "weeks":
        if recurrence_days:
            current_weekday = base_date.weekday()  # 0=Monday, 6=Sunday
            sorted_days = sorted(recurrence_days)

            # Find next day in the same week
            next_day_this_week = None
            for day in sorted_days:
                if day > current_weekday:
                    next_day_this_week = day
                    break

            if next_day_this_week is not None:
                # There's a later day this week
                days_ahead = next_day_this_week - current_weekday
            else:
                # No more days this week, jump to first day of next interval
                days_until_next_interval = (7 - current_weekday) + (recurrence_interval - 1) * 7
                days_ahead = days_until_next_interval + sorted_days[0]

            return base_date + timedelta(days=days_ahead)
        else:
            return base_date + timedelta(weeks=recurrence_interval)

    elif recurrence_unit == "months":
        target_month = base_date.month + recurrence_interval
        target_year = base_date.year

        while target_month > 12:
            target_month -= 12
            target_year += 1

        max_day = calendar.monthrange(target_year, target_month)[1]
        target_day = min(base_date.day, max_day)

        return base_date.replace(year=target_year, month=target_month, day=target_day)

    elif recurrence_unit == "years":
        target_year = base_date.year + recurrence_interval
        target_day = base_date.day

        if base_date.month == 2 and base_date.day == 29 and not calendar.isleap(target_year):
            target_day = 28

        return base_date.replace(year=target_year, day=target_day)

    return base_date + timedelta(days=1)


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
        raise LabelNotFoundException()
    return labels
