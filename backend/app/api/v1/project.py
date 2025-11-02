from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.api.v1.auth_deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectsReorder, ProjectUpdate
from app.services import project_service

router = APIRouter()


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProjectResponse:
    """Create a new project for the authenticated user."""
    new_project = await project_service.create_project(
        db=db,
        user_id=current_user.id,
        title=project_data.title,
        parent_id=project_data.parent_id,
        order_index=project_data.order_index,
    )
    return ProjectResponse.model_validate(new_project)


@router.get("/", response_model=list[ProjectResponse], status_code=status.HTTP_200_OK)
async def get_projects(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[ProjectResponse]:
    """Get all projects for the authenticated user."""
    projects = await project_service.get_projects(db=db, user_id=current_user.id)
    return [ProjectResponse.model_validate(project) for project in projects]


@router.get("/{project_id}", response_model=ProjectResponse, status_code=status.HTTP_200_OK)
async def get_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProjectResponse:
    """Get a specific project by ID for the authenticated user."""
    project = await project_service.get_project_by_id(db=db, project_id=project_id, user_id=current_user.id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return ProjectResponse.model_validate(project)


@router.patch("/reorder", status_code=status.HTTP_204_NO_CONTENT)
async def reorder_projects(
    projects_reorder: list[ProjectsReorder],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Batch update project order and parent relationships."""
    try:
        await project_service.reorder_projects(
            db=db,
            user_id=current_user.id,
            projects_reorder=projects_reorder
        )
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="One or more projects not found") from None


@router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK
)
async def update_project(
    project_id: UUID,
    project_data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProjectResponse:
    """Update a specific project by ID for the authenticated user."""
    try:
        updated_project = await project_service.update_project(
            db=db,
            project_id=project_id,
            user_id=current_user.id,
            parent_id=project_data.parent_id,
            title=project_data.title,
            order_index=project_data.order_index,
        )
        return ProjectResponse.model_validate(updated_project)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found") from None


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a specific project by ID for the authenticated user."""
    try:
        await project_service.delete_project(db=db, project_id=project_id, user_id=current_user.id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found") from None
