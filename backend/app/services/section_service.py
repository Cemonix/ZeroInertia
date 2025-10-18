from collections.abc import Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select

from app.models.section import Section
from app.schemas.section import SectionReorder


async def create_section(db: AsyncSession, user_id: UUID, title: str, project_id: UUID | None, order_index: int) -> Section:
    """Create a new section for a user."""
    new_section = Section(
        user_id=user_id,
        title=title,
        order_index=order_index,
        project_id=project_id
    )
    db.add(new_section)
    await db.commit()
    await db.refresh(new_section)
    return new_section


async def get_section_by_id(db: AsyncSession, section_id: UUID, user_id: UUID) -> Section | None:
    """Retrieve a section by its ID and user ID."""
    result = await db.execute(
        select(Section).where(Section.id == section_id, Section.user_id == user_id)
    )
    return result.scalars().first()


async def get_sections(db: AsyncSession, user_id: UUID) -> Sequence[Section]:
    """Retrieve all sections for a specific user."""
    result = await db.execute(
        select(Section).where(Section.user_id == user_id).order_by(Section.created_at.desc())
    )
    return result.scalars().all()


async def get_sections_by_project(db: AsyncSession, user_id: UUID, project_id: UUID) -> Sequence[Section]:
    """Retrieve all sections for a specific project and user."""
    result = await db.execute(
        select(Section).where(
            Section.user_id == user_id,
            Section.project_id == project_id
        ).order_by(Section.created_at.desc())
    )
    return result.scalars().all()


async def update_section(
    db: AsyncSession,
    section_id: UUID,
    user_id: UUID,
    title: str | None = None,
    order_index: int | None = None,
) -> Section:
    """Update an existing section."""
    section = await get_section_by_id(db, section_id, user_id)
    if section is None:
        raise ValueError("Section not found")

    if title is not None:
        section.title = title
    if order_index is not None:
        section.order_index = order_index

    db.add(section)
    await db.commit()
    await db.refresh(section)
    return section


async def delete_section(db: AsyncSession, section_id: UUID, user_id: UUID) -> None:
    """Delete a section."""
    section = await get_section_by_id(db, section_id, user_id)
    if section is None:
        raise ValueError("Section not found")

    await db.delete(section)
    await db.commit()


async def reorder_sections(db: AsyncSession, user_id: UUID, sections_reorder: list[SectionReorder]) -> None:
    """Reorder sections based on the provided list of section data."""
    section_ids = [s.id for s in sections_reorder]

    result = await db.execute(
        select(Section).where(
            Section.id.in_(section_ids),
            Section.user_id == user_id
        )
    )
    sections = {s.id: s for s in result.scalars().all()}

    if len(sections) != len(section_ids):
        raise ValueError("One or more sections not found")

    for section_data in sections_reorder:
        section = sections[section_data.id]
        section.order_index = section_data.order_index
        db.add(section)

    await db.commit()
