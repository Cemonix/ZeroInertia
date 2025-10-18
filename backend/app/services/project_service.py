from collections.abc import Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select

from app.models import Section
from app.models.project import Project
from app.schemas.project import ProjectsReorder


async def create_project(db: AsyncSession, user_id: UUID, title: str, parent_id: UUID | None, order_index: int) -> Project:
    """Create a new project for a user."""
    new_project = Project(
        user_id=user_id,
        title=title,
        order_index=order_index,
        parent_id=parent_id
    )
    db.add(new_project)
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
    parent_id: UUID | None = None,
    title: str | None = None,
    order_index: int | None = None,
) -> Project:
    """Update an existing project."""
    project = await get_project_by_id(db, project_id, user_id)
    if project is None:
        raise ValueError("Project not found")

    if parent_id is not None:
        project.parent_id = parent_id
    if title is not None:
        project.title = title
    if order_index is not None:
        project.order_index = order_index

    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


async def delete_project(db: AsyncSession, project_id: UUID, user_id: UUID) -> None:
    """Delete a project."""
    project = await get_project_by_id(db, project_id, user_id)
    if project is None:
        raise ValueError("Project not found")

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
        raise ValueError("One or more projects not found")

    for project_data in projects_reorder:
        project = projects[project_data.id]
        project.parent_id = project_data.parent_id
        project.order_index = project_data.order_index
        db.add(project)

    await db.commit()
