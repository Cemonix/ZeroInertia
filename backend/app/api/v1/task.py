from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.api.v1.auth import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
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
        section_id=task_data.section_id
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
            is_done=task_data.is_done
        )
        return TaskResponse.model_validate(updated_task)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found") from None


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
