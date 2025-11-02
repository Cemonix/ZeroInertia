from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.api.v1.auth_deps import get_current_user
from app.core.database import get_db
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
    try:
        new_task = await task_service.create_task(
            db=db,
            user_id=current_user.id,
            title=task_data.title,
            description=task_data.description,
            project_id=task_data.project_id,
            section_id=task_data.section_id,
            priority_id=task_data.priority_id,
            due_datetime=task_data.due_datetime,
            label_ids=task_data.label_ids,
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
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
    try:
        updated_task = await task_service.update_task(
            db=db,
            task_id=task_id,
            user_id=current_user.id,
            title=task_data.title,
            description=task_data.description,
            completed=task_data.completed,
            priority_id=task_data.priority_id,
            due_datetime=task_data.due_datetime,
            label_ids=task_data.label_ids,
        )
        return TaskResponse.model_validate(updated_task)
    except ValueError as exc:
        message = str(exc)
        if message == "Task not found":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message) from exc
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message) from exc


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a specific task by ID for the authenticated user."""
    try:
        await task_service.delete_task(db=db, task_id=task_id, user_id=current_user.id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found") from None


@router.post("/reorder", status_code=status.HTTP_204_NO_CONTENT)
async def reorder_tasks(
    tasks_reorder: list[TaskReorder],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Reorder tasks for the authenticated user."""
    try:
        await task_service.reorder_tasks(
            db=db,
            user_id=current_user.id,
            tasks_reorder=tasks_reorder
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from None


@router.post("/{task_id}/archive", status_code=status.HTTP_204_NO_CONTENT)
async def archive_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Archive a specific task by ID for the authenticated user."""
    try:
        await task_service.archive_task(db=db, task_id=task_id, user_id=current_user.id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found") from None
