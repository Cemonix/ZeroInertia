from datetime import datetime
from uuid import UUID

from fastapi import Depends, Query, status
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.api.v1.auth_deps import get_current_user
from app.api.v1.pagination_deps import get_pagination_params
from app.core.database import get_db
from app.core.exceptions import TaskNotFoundException
from app.models.user import User
from app.schemas.pagination import PaginatedResponse, PaginationParams
from app.schemas.task import (
    TaskCountsByProjectResponse,
    TaskCreate,
    TaskReorder,
    TaskResponse,
    TaskUpdate,
)
from app.services import task_service

router = APIRouter()


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TaskResponse:
    """Create a new task for the authenticated user."""
    new_task = await task_service.create_task(
        db=db,
        user_id=current_user.id,
        title=task_data.title,
        description=task_data.description,
        project_id=task_data.project_id,
        section_id=task_data.section_id,
        priority_id=task_data.priority_id,
        due_datetime=task_data.due_datetime,
        recurrence_interval=task_data.recurrence_interval,
        recurrence_unit=task_data.recurrence_unit,
        recurrence_days=task_data.recurrence_days,
        label_ids=task_data.label_ids,
        reminder_minutes=task_data.reminder_minutes,
        duration_minutes=task_data.duration_minutes,
    )
    return TaskResponse.model_validate(new_task)


@router.get("/", response_model=PaginatedResponse[TaskResponse])
async def get_tasks(
    project_id: UUID | None = None,
    pagination: PaginationParams = Depends(get_pagination_params),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[TaskResponse]:
    """
    Get tasks for the authenticated user with pagination.

    Optionally filtered by project_id.
    """
    if project_id:
        tasks, total = await task_service.get_tasks_by_project(
            db=db,
            user_id=current_user.id,
            project_id=project_id,
            skip=pagination.offset,
            limit=pagination.limit,
        )
    else:
        tasks, total = await task_service.get_tasks(
            db=db,
            user_id=current_user.id,
            skip=pagination.offset,
            limit=pagination.limit,
        )

    task_responses = [TaskResponse.model_validate(task) for task in tasks]
    return PaginatedResponse[TaskResponse].create(
        items=task_responses,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    )


@router.get("/by-date", response_model=list[TaskResponse])
async def get_tasks_by_date_range(
    date_from: datetime = Query(..., description="Start of date range (inclusive)"),
    date_to: datetime = Query(..., description="End of date range (exclusive)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[TaskResponse]:
    """Get tasks for the authenticated user within a specific date range."""
    tasks = await task_service.get_tasks_by_date_range(
        db=db,
        user_id=current_user.id,
        date_from=date_from,
        date_to=date_to,
    )
    return [TaskResponse.model_validate(task) for task in tasks]


@router.get("/counts", response_model=TaskCountsByProjectResponse, status_code=status.HTTP_200_OK)
async def get_task_counts_by_project(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TaskCountsByProjectResponse:
    """Get counts of active tasks grouped by project for the authenticated user."""
    counts = await task_service.get_active_task_counts_by_project(db=db, user_id=current_user.id)
    return TaskCountsByProjectResponse(counts=counts)


@router.get("/archived", response_model=PaginatedResponse[TaskResponse])
async def get_archived_tasks(
    pagination: PaginationParams = Depends(get_pagination_params),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[TaskResponse]:
    """Get archived tasks for the authenticated user with pagination."""
    tasks, total = await task_service.get_archived_tasks(
        db=db,
        user_id=current_user.id,
        skip=pagination.offset,
        limit=pagination.limit,
    )

    task_responses = [TaskResponse.model_validate(task) for task in tasks]
    return PaginatedResponse[TaskResponse].create(
        items=task_responses,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    )


@router.get("/{task_id}", response_model=TaskResponse, status_code=status.HTTP_200_OK)
async def get_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TaskResponse:
    """Get a specific task by ID for the authenticated user."""
    task = await task_service.get_task_by_id(db=db, task_id=task_id, user_id=current_user.id)
    if not task:
        raise TaskNotFoundException(str(task_id))
    return TaskResponse.model_validate(task)


@router.patch(
    "/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK
)
async def update_task(
    task_id: UUID,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TaskResponse:
    """Update a specific task by ID for the authenticated user."""
    updated_task = await task_service.update_task(
        db=db,
        task_id=task_id,
        user_id=current_user.id,
        update_data=task_data,
    )
    return TaskResponse.model_validate(updated_task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a specific task by ID for the authenticated user."""
    await task_service.delete_task(db=db, task_id=task_id, user_id=current_user.id)


@router.post("/reorder", status_code=status.HTTP_204_NO_CONTENT)
async def reorder_tasks(
    tasks_reorder: list[TaskReorder],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Reorder tasks for the authenticated user."""
    await task_service.reorder_tasks(
        db=db,
        user_id=current_user.id,
        tasks_reorder=tasks_reorder
    )


@router.post("/{task_id}/archive", status_code=status.HTTP_204_NO_CONTENT)
async def archive_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Archive a specific task by ID for the authenticated user."""
    await task_service.archive_task(db=db, task_id=task_id, user_id=current_user.id)


@router.post(
    "/{task_id}/snooze",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
)
async def snooze_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TaskResponse:
    """Snooze a specific task by ID for the authenticated user."""
    snoozed_task = await task_service.snooze_task(
        db=db,
        task_id=task_id,
        user_id=current_user.id,
    )
    return TaskResponse.model_validate(snoozed_task)
