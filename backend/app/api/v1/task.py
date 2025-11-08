from uuid import UUID

from fastapi import Depends, status
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.api.v1.auth_deps import get_current_user
from app.core.database import get_db
from app.core.exceptions import TaskNotFoundException
from app.models.user import User
from app.schemas.task import TaskCreate, TaskReorder, TaskResponse, TaskUpdate
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
        recurrence_type=task_data.recurrence_type,
        recurrence_days=task_data.recurrence_days,
        label_ids=task_data.label_ids,
        reminder_minutes=task_data.reminder_minutes,
    )
    return TaskResponse.model_validate(new_task)


@router.get("/", response_model=list[TaskResponse])
async def get_tasks(
    project_id: UUID | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[TaskResponse]:
    """Get tasks for the authenticated user, optionally filtered by project_id."""
    if project_id:
        tasks = await task_service.get_tasks_by_project(
            db=db, user_id=current_user.id, project_id=project_id
        )
    else:
        tasks = await task_service.get_tasks(db=db, user_id=current_user.id)
    return [TaskResponse.model_validate(task) for task in tasks]


@router.get("/archived", response_model=list[TaskResponse])
async def get_archived_tasks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[TaskResponse]:
    """Get all archived tasks for the authenticated user."""
    tasks = await task_service.get_archived_tasks(db=db, user_id=current_user.id)
    return [TaskResponse.model_validate(task) for task in tasks]


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
    # Only pass fields that were explicitly set in the request
    # This allows null values to clear fields (e.g., removing a due date)
    update_fields = task_data.model_dump(exclude_unset=True)
    updated_task = await task_service.update_task(
        db=db,
        task_id=task_id,
        user_id=current_user.id,
        **update_fields,  # pyright: ignore[reportAny]
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
