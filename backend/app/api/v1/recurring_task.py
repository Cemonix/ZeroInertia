from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.api.v1.auth_deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.recurring_task import (
    RecurringTaskCreate,
    RecurringTaskResponse,
    RecurringTaskUpdate,
)
from app.services import recurring_task_service

router = APIRouter()


@router.post("/", response_model=RecurringTaskResponse, status_code=status.HTTP_201_CREATED)
async def create_recurring_task(
    recurring_task_data: RecurringTaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> RecurringTaskResponse:
    """Create a new recurring task for the authenticated user."""
    try:
        new_recurring_task = await recurring_task_service.create_recurring_task(
            db=db,
            user_id=current_user.id,
            title=recurring_task_data.title,
            description=recurring_task_data.description,
            project_id=recurring_task_data.project_id,
            section_id=recurring_task_data.section_id,
            recurrence_type=recurring_task_data.recurrence_type,
            recurrence_days=recurring_task_data.recurrence_days,
            recurrence_time=recurring_task_data.recurrence_time,
            start_date=recurring_task_data.start_date,
            end_date=recurring_task_data.end_date,
            priority_id=recurring_task_data.priority_id,
            label_ids=recurring_task_data.label_ids,
            is_active=recurring_task_data.is_active,
        )
    except ValueError as exc:
        # Check if this is a "not found" error (from foreign key constraint)
        error_msg = str(exc).lower()
        if "not found" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc)
            ) from exc
        # Other validation errors return 400
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        ) from exc
    return RecurringTaskResponse.model_validate(new_recurring_task)


@router.get("/", response_model=list[RecurringTaskResponse])
async def get_recurring_tasks(
    project_id: UUID | None = None,
    include_inactive: bool = False,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[RecurringTaskResponse]:
    """Get recurring tasks for the authenticated user, optionally filtered by project_id."""
    if project_id:
        recurring_tasks = await recurring_task_service.get_recurring_tasks_by_project(
            db=db, user_id=current_user.id, project_id=project_id, include_inactive=include_inactive
        )
    else:
        recurring_tasks = await recurring_task_service.get_recurring_tasks(
            db=db, user_id=current_user.id, include_inactive=include_inactive
        )
    return [RecurringTaskResponse.model_validate(rt) for rt in recurring_tasks]


@router.get("/{recurring_task_id}", response_model=RecurringTaskResponse, status_code=status.HTTP_200_OK)
async def get_recurring_task(
    recurring_task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> RecurringTaskResponse:
    """Get a specific recurring task by ID for the authenticated user."""
    recurring_task = await recurring_task_service.get_recurring_task_by_id(
        db=db, recurring_task_id=recurring_task_id, user_id=current_user.id
    )
    if not recurring_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recurring task not found")
    return RecurringTaskResponse.model_validate(recurring_task)


@router.patch(
    "/{recurring_task_id}",
    response_model=RecurringTaskResponse,
    status_code=status.HTTP_200_OK
)
async def update_recurring_task(
    recurring_task_id: UUID,
    recurring_task_data: RecurringTaskUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> RecurringTaskResponse:
    """Update a specific recurring task by ID for the authenticated user."""
    try:
        updated_recurring_task = await recurring_task_service.update_recurring_task(
            db=db,
            recurring_task_id=recurring_task_id,
            user_id=current_user.id,
            update_data=recurring_task_data,
        )
        return RecurringTaskResponse.model_validate(updated_recurring_task)
    except ValueError as exc:
        message = str(exc)
        if message == "Recurring task not found":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message) from exc
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message) from exc


@router.delete("/{recurring_task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recurring_task(
    recurring_task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a specific recurring task by ID for the authenticated user."""
    try:
        await recurring_task_service.delete_recurring_task(
            db=db, recurring_task_id=recurring_task_id, user_id=current_user.id
        )
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recurring task not found") from None


@router.post("/{recurring_task_id}/pause", response_model=RecurringTaskResponse, status_code=status.HTTP_200_OK)
async def pause_recurring_task(
    recurring_task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> RecurringTaskResponse:
    """Pause (deactivate) a specific recurring task by ID for the authenticated user."""
    try:
        recurring_task = await recurring_task_service.pause_recurring_task(
            db=db, recurring_task_id=recurring_task_id, user_id=current_user.id
        )
        return RecurringTaskResponse.model_validate(recurring_task)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recurring task not found") from None


@router.post("/{recurring_task_id}/resume", response_model=RecurringTaskResponse, status_code=status.HTTP_200_OK)
async def resume_recurring_task(
    recurring_task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> RecurringTaskResponse:
    """Resume (activate) a specific recurring task by ID for the authenticated user."""
    try:
        recurring_task = await recurring_task_service.resume_recurring_task(
            db=db, recurring_task_id=recurring_task_id, user_id=current_user.id
        )
        return RecurringTaskResponse.model_validate(recurring_task)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recurring task not found") from None
