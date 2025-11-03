from collections.abc import Sequence
from datetime import date, datetime, time, timezone
from typing import Any, cast
from uuid import UUID, uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import insert, select, update

from app.core.logging import logger
from app.models.recurring_task import RecurringTask
from app.models.task import Task
from app.schemas.recurring_task import RecurrenceTypeEnum, RecurringTaskUpdate
from app.services import task_service


async def create_recurring_task(
    db: AsyncSession,
    user_id: UUID,
    title: str,
    description: str | None,
    project_id: UUID,
    section_id: UUID,
    recurrence_type: RecurrenceTypeEnum,
    recurrence_days: list[int] | None,
    recurrence_time: time,
    start_date: date,
    end_date: date | None = None,
    priority_id: UUID | None = None,
    label_ids: list[UUID] | None = None,
    is_active: bool = True,
) -> RecurringTask:
    """Create a new recurring task for a user."""
    _validate_recurrence_inputs(recurrence_type, recurrence_days)
    normalized_days = _normalize_recurrence_days(recurrence_days)

    new_recurring_task = RecurringTask(
        user_id=user_id,
        title=title,
        description=description,
        project_id=project_id,
        section_id=section_id,
        recurrence_type=recurrence_type,
        recurrence_days=normalized_days,
        recurrence_time=recurrence_time,
        start_date=start_date,
        end_date=end_date,
        priority_id=priority_id,
        label_ids=label_ids,
        is_active=is_active,
        last_generated_date=None,
    )

    db.add(new_recurring_task)

    try:
        await db.commit()
    except IntegrityError as e:
        await db.rollback()
        # Parse the error to provide helpful feedback
        error_msg = str(e.orig) if hasattr(e, "orig") else str(e)
        if "section_id" in error_msg:
            raise ValueError("Section not found or does not belong to you") from e
        elif "project_id" in error_msg:
            raise ValueError("Project not found or does not belong to you") from e
        elif "priority_id" in error_msg:
            raise ValueError("Priority not found") from e
        else:
            raise ValueError("Invalid reference: one or more related entities not found") from e

    await db.refresh(new_recurring_task)
    return new_recurring_task


async def get_recurring_task_by_id(
    db: AsyncSession, recurring_task_id: UUID, user_id: UUID
) -> RecurringTask | None:
    """Retrieve a recurring task by its ID and user ID."""
    result = await db.execute(
        select(RecurringTask).where(
            RecurringTask.id == recurring_task_id, RecurringTask.user_id == user_id
        )
    )
    return result.scalars().first()


async def get_recurring_tasks(
    db: AsyncSession, user_id: UUID, include_inactive: bool = False
) -> Sequence[RecurringTask]:
    """Retrieve all recurring tasks for a specific user."""
    query = select(RecurringTask).where(RecurringTask.user_id == user_id)

    if not include_inactive:
        query = query.where(RecurringTask.is_active == True)  # noqa: E712

    query = query.order_by(RecurringTask.created_at.desc())

    result = await db.execute(query)
    return result.scalars().all()


async def get_recurring_tasks_by_project(
    db: AsyncSession, user_id: UUID, project_id: UUID, include_inactive: bool = False
) -> Sequence[RecurringTask]:
    """Retrieve all recurring tasks for a specific project and user."""
    query = select(RecurringTask).where(
        RecurringTask.user_id == user_id, RecurringTask.project_id == project_id
    )

    if not include_inactive:
        query = query.where(RecurringTask.is_active == True)  # noqa: E712

    query = query.order_by(RecurringTask.created_at.desc())

    result = await db.execute(query)
    return result.scalars().all()


async def update_recurring_task(
    db: AsyncSession,
    recurring_task_id: UUID,
    user_id: UUID,
    update_data: RecurringTaskUpdate,
) -> RecurringTask:
    """Update an existing recurring task."""
    recurring_task = await get_recurring_task_by_id(db, recurring_task_id, user_id)
    if recurring_task is None:
        raise ValueError("Recurring task not found")

    # Update only provided fields
    update_dict = update_data.model_dump(exclude_unset=True)

    if "recurrence_type" in update_dict or "recurrence_days" in update_dict:
        new_type = cast(
            RecurrenceTypeEnum, update_dict.get("recurrence_type", recurring_task.recurrence_type)
        )
        new_days = cast(
            list[int], update_dict.get("recurrence_days", recurring_task.recurrence_days)
        )
        _validate_recurrence_inputs(new_type, new_days)
        update_dict["recurrence_days"] = _normalize_recurrence_days(new_days)

    for key, value in update_dict.items():  # pyright: ignore[reportAny]
        setattr(recurring_task, key, value)

    db.add(recurring_task)
    await db.commit()
    await db.refresh(recurring_task)

    return recurring_task


async def delete_recurring_task(
    db: AsyncSession, recurring_task_id: UUID, user_id: UUID
) -> None:
    """Delete a recurring task."""
    recurring_task = await get_recurring_task_by_id(db, recurring_task_id, user_id)
    if recurring_task is None:
        raise ValueError("Recurring task not found")

    await db.delete(recurring_task)
    await db.commit()


async def pause_recurring_task(
    db: AsyncSession, recurring_task_id: UUID, user_id: UUID
) -> RecurringTask:
    """Pause (deactivate) a recurring task."""
    recurring_task = await get_recurring_task_by_id(db, recurring_task_id, user_id)
    if recurring_task is None:
        raise ValueError("Recurring task not found")

    recurring_task.is_active = False
    db.add(recurring_task)
    await db.commit()
    await db.refresh(recurring_task)

    return recurring_task


async def resume_recurring_task(
    db: AsyncSession, recurring_task_id: UUID, user_id: UUID
) -> RecurringTask:
    """Resume (activate) a recurring task."""
    recurring_task = await get_recurring_task_by_id(db, recurring_task_id, user_id)
    if recurring_task is None:
        raise ValueError("Recurring task not found")

    recurring_task.is_active = True
    db.add(recurring_task)
    await db.commit()
    await db.refresh(recurring_task)

    return recurring_task


def should_generate_task_today(recurring_task: RecurringTask, today: date) -> bool:
    """
    Determine if a task should be generated today based on recurrence pattern.

    Args:
        recurring_task: The recurring task configuration
        today: The date to check

    Returns:
        True if a task should be generated, False otherwise
    """
    # Check if active
    if not recurring_task.is_active:
        return False

    # Check if we're within the date range
    if today < recurring_task.start_date:
        return False
    if recurring_task.end_date and today > recurring_task.end_date:
        return False

    # Check if already generated today
    if recurring_task.last_generated_date == today:
        return False

    # Check recurrence pattern
    recurrence_type = recurring_task.recurrence_type
    weekday = today.weekday()  # 0=Monday, 6=Sunday

    if recurrence_type == "daily":
        return True

    elif recurrence_type == "weekly":
        if recurring_task.recurrence_days is None:
            return False
        return weekday in recurring_task.recurrence_days

    elif recurrence_type == "alternate_days":
        if recurring_task.last_generated_date is None:
            return True
        days_since_last = (today - recurring_task.last_generated_date).days
        return days_since_last >= 2

    return False


async def generate_task_from_recurring(
    db: AsyncSession, recurring_task: RecurringTask, generation_date: date
) -> Task:
    """
    Generate a new task instance from a recurring task template.

    Args:
        db: Database session
        recurring_task: The recurring task template
        generation_date: The date for which to generate the task

    Returns:
        The newly created task
    """
    # Combine generation date with recurrence time to create due datetime
    due_datetime = datetime.combine(generation_date, recurring_task.recurrence_time)
    # Make it timezone-aware (UTC)
    due_datetime = due_datetime.replace(tzinfo=timezone.utc)

    # Create the task using the task service
    new_task = await task_service.create_task(
        db=db,
        user_id=recurring_task.user_id,
        title=recurring_task.title,
        description=recurring_task.description,
        project_id=recurring_task.project_id,
        section_id=recurring_task.section_id,
        priority_id=recurring_task.priority_id,
        due_datetime=due_datetime,
        label_ids=list(recurring_task.label_ids) if recurring_task.label_ids else None,
    )

    # Update last_generated_date
    recurring_task.last_generated_date = generation_date
    db.add(recurring_task)
    await db.commit()

    return new_task


async def generate_all_recurring_tasks(
    db: AsyncSession, generation_date: date | None = None
) -> int:
    """
    Generate tasks for all active recurring tasks that should run today.

    This function is called by the scheduler job and uses bulk operations
    for better performance.

    Args:
        db: Database session
        generation_date: The date to generate tasks for (defaults to today)

    Returns:
        Number of tasks generated
    """
    import time
    start_time = time.time()

    if generation_date is None:
        generation_date = date.today()

    logger.info(f"Starting recurring task generation for date: {generation_date}")

    # Get all active recurring tasks with optimized query
    result = await db.execute(
        select(RecurringTask)
        .where(
            RecurringTask.is_active == True,  # noqa: E712
            # Only consider tasks that might be due
            RecurringTask.start_date <= generation_date,
            # Exclude tasks that have ended
            (RecurringTask.end_date.is_(None) | (RecurringTask.end_date >= generation_date))
        )
    )
    recurring_tasks = result.scalars().all()

    logger.info(f"Found {len(recurring_tasks)} active recurring tasks to evaluate")

    # Prepare bulk data
    tasks_to_insert: list[dict[str, Any]] = []  # pyright: ignore[reportExplicitAny]
    recurring_task_updates: list[dict[str, UUID | date]] = []
    errors: list[dict[str, str]] = []

    for recurring_task in recurring_tasks:
        if not should_generate_task_today(recurring_task, generation_date):
            continue

        # Check if there's an incomplete task from this recurring template
        # If so, skip generation
        incomplete_check = await db.execute(
            select(Task.id)
            .where(
                Task.recurring_task_id == recurring_task.id,
                Task.completed == False,  # noqa: E712
                Task.archived == False,  # noqa: E712
            )
            .limit(1)
        )
        has_incomplete = incomplete_check.scalar() is not None

        if has_incomplete:
            logger.debug(
                f"Skipping generation for recurring task {recurring_task.id} " +
                f"({recurring_task.title}) - previous task is still incomplete"
            )
            continue

        try:
            # Get order index for the section
            order_result = await db.execute(
                select(Task.order_index)
                .where(Task.section_id == recurring_task.section_id, Task.user_id == recurring_task.user_id)
                .order_by(Task.order_index.desc())
                .limit(1)
            )
            max_order = order_result.scalar()
            next_order_index = (max_order + 1) if max_order is not None else 0

            # Prepare task data for bulk insert
            due_datetime = datetime.combine(generation_date, recurring_task.recurrence_time)
            due_datetime = due_datetime.replace(tzinfo=timezone.utc)

            task_data = {
                "id": uuid4(),
                "user_id": recurring_task.user_id,
                "title": recurring_task.title,
                "description": recurring_task.description,
                "project_id": recurring_task.project_id,
                "section_id": recurring_task.section_id,
                "priority_id": recurring_task.priority_id,
                "recurring_task_id": recurring_task.id,
                "due_datetime": due_datetime,
                "completed": False,
                "archived": False,
                "order_index": next_order_index,
            }
            tasks_to_insert.append(task_data)

            # Track recurring task to update
            recurring_task_updates.append({
                "id": recurring_task.id,
                "last_generated_date": generation_date,
            })

        except Exception as exc:
            error_msg = f"Error preparing task for recurring task {recurring_task.id}: {exc}"
            logger.error(error_msg, exc_info=True)
            errors.append({
                "recurring_task_id": str(recurring_task.id),
                "title": recurring_task.title,
                "error": str(exc),
            })

    # Bulk insert tasks
    if tasks_to_insert:
        try:
            _ = await db.execute(insert(Task), tasks_to_insert)
            logger.info(f"Bulk inserted {len(tasks_to_insert)} tasks")
        except Exception as exc:
            logger.error(f"Bulk insert failed, falling back to individual inserts: {exc}")
            # Fallback to individual inserts if bulk fails
            tasks_to_insert = []
            for task_data in tasks_to_insert:
                try:
                    _ = await db.execute(insert(Task).values(**task_data))
                except Exception as individual_exc:
                    logger.error(f"Failed to insert task: {individual_exc}")

    # Bulk update recurring tasks
    if recurring_task_updates:
        try:
            _ = await db.execute(
                update(RecurringTask),
                recurring_task_updates
            )
            logger.info(f"Updated last_generated_date for {len(recurring_task_updates)} recurring tasks")
        except Exception as exc:
            logger.error(f"Bulk update of recurring tasks failed: {exc}")

    # Commit all changes
    try:
        await db.commit()
    except Exception as exc:
        await db.rollback()
        logger.error(f"Failed to commit recurring task generation: {exc}")
        raise

    elapsed = time.time() - start_time
    tasks_generated = len(tasks_to_insert)

    logger.info(
        "Recurring task generation completed: " +
        f"{tasks_generated} tasks generated, " +
        f"{len(errors)} errors, " +
        f"took {elapsed:.2f}s"
    )

    if elapsed > 5.0:
        logger.warning(f"Recurring task generation took longer than expected: {elapsed:.2f}s")

    if errors:
        logger.warning(f"Encountered {len(errors)} errors during generation: {errors}")

    return tasks_generated


def _normalize_recurrence_days(days: list[int] | None) -> list[int] | None:
    """Sort and deduplicate recurrence days."""
    if days is None:
        return None
    unique_days = sorted(set(days))
    return unique_days or None


def _validate_recurrence_inputs(
    recurrence_type: RecurrenceTypeEnum,
    recurrence_days: list[int] | None,
) -> None:
    """Ensure recurrence configuration is coherent before persisting."""
    if recurrence_type == "weekly":
        if not recurrence_days:
            raise ValueError("recurrence_days must contain at least one day for weekly recurrence")
        invalid_days = [day for day in recurrence_days if day < 0 or day > 6]
        if invalid_days:
            raise ValueError("recurrence_days must contain integers between 0 and 6")
    else:
        if recurrence_days not in (None, []):
            raise ValueError("recurrence_days is only allowed for weekly recurrence")
