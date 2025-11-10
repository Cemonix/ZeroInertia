from collections.abc import Sequence
from typing import cast
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select

from app.core.exceptions import CircularReferenceException, ProjectNotFoundException
from app.models import Section
from app.models.project import Project
from app.schemas.project import ProjectsReorder


async def create_project(db: AsyncSession, user_id: UUID, title: str, parent_id: UUID | None, order_index: int) -> Project:
    """Create a new project for a user."""
    # Create project with a temporary ID to check for circular references
    new_project = Project(
        user_id=user_id,
        title=title,
        order_index=order_index,
        parent_id=parent_id
    )
    db.add(new_project)
    await db.flush()  # Generate ID without committing

    # Check for circular reference
    if await _check_circular_reference(db, new_project.id, parent_id):
        await db.rollback()
        raise CircularReferenceException(
            "Cannot set parent: this would create a circular reference in the project hierarchy"
        )

    await db.commit()

    # When project is created, also create a default section "Default"
    default_section = Section(
        title="Default",
        project_id=new_project.id,
        user_id=user_id
    )
    db.add(default_section)
    await db.commit()

    await db.refresh(new_project)
    return new_project


async def get_project_by_id(db: AsyncSession, project_id: UUID, user_id: UUID) -> Project | None:
    """Retrieve a project by its ID and user ID."""
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.user_id == user_id)
    )
    return result.scalars().first()


async def get_projects(db: AsyncSession, user_id: UUID) -> Sequence[Project]:
    """Retrieve all projects for a specific user."""
    result = await db.execute(
        select(Project).where(Project.user_id == user_id).order_by(Project.created_at.desc())
    )
    return result.scalars().all()


async def update_project(
    db: AsyncSession,
    project_id: UUID,
    user_id: UUID,
    **updates: UUID | str | int | None,
) -> Project:
    """
    Update an existing project.

    Args:
        db: Database session
        project_id: ID of project to update
        user_id: ID of user who owns the project
        **updates: Fields to update (parent_id, title, order_index)
    """
    project = await get_project_by_id(db, project_id, user_id)
    if project is None:
        raise ProjectNotFoundException(str(project_id))

    # Handle parent_id updates if provided
    if "parent_id" in updates:
        parent_id = updates["parent_id"]
        # Check for circular reference if setting a non-null parent
        if (
            parent_id is not None
            and parent_id != project.parent_id
            and await _check_circular_reference(db, project_id, cast(UUID, parent_id))
        ):
            raise CircularReferenceException(
                "Cannot set parent: this would create a circular reference in the project hierarchy"
            )
        # Update parent_id (can be None to remove parent, or a UUID to set parent)
        project.parent_id = cast(UUID | None, parent_id)

    if "title" in updates:
        project.title = cast(str, updates["title"])
    if "order_index" in updates:
        project.order_index = cast(int, updates["order_index"])

    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


async def delete_project(db: AsyncSession, project_id: UUID, user_id: UUID) -> None:
    """Delete a project."""
    project = await get_project_by_id(db, project_id, user_id)
    if project is None:
        raise ProjectNotFoundException(str(project_id))

    await db.delete(project)
    await db.commit()


async def reorder_projects(db: AsyncSession, user_id: UUID, projects_reorder: list[ProjectsReorder]) -> None:
    """Reorder projects based on the provided list of project data."""
    project_ids = [p.id for p in projects_reorder]

    result = await db.execute(
        select(Project).where(
            Project.id.in_(project_ids),
            Project.user_id == user_id
        )
    )
    projects = {p.id: p for p in result.scalars().all()}

    if len(projects) != len(project_ids):
        raise ProjectNotFoundException()

    # Check for circular references before applying any changes
    for project_data in projects_reorder:
        if (
            project_data.parent_id is not None
            and await _check_circular_reference(db, project_data.id, project_data.parent_id)
        ):
                raise CircularReferenceException(
                    f"Cannot reorder: setting parent for project {project_data.id} would create a circular reference"
                )

    # Apply updates after all validation passes
    for project_data in projects_reorder:
        project = projects[project_data.id]
        project.parent_id = project_data.parent_id
        project.order_index = project_data.order_index
        db.add(project)

    await db.commit()


async def _check_circular_reference(
    db: AsyncSession,
    project_id: UUID,
    new_parent_id: UUID | None
) -> bool:
    """
    Check if setting new_parent_id would create a circular reference.

    Returns True if circular reference detected, False otherwise.
    """
    if new_parent_id is None:
        return False

    # A project cannot be its own parent
    if project_id == new_parent_id:
        return True

    # Traverse up the parent chain to check for cycles
    current_id = new_parent_id
    visited = {project_id}

    while current_id:
        if current_id in visited:
            return True  # Circular reference detected
        visited.add(current_id)

        result = await db.execute(
            select(Project.parent_id).where(Project.id == current_id)
        )
        parent = result.scalar_one_or_none()
        current_id = parent

    return False
