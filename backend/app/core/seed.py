"""Database seeding utilities for initializing default data."""
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_local
from app.core.logging import logger
from app.models.priority import Priority
from app.models.project import Project
from app.models.section import Section

DEFAULT_PRIORITIES = [
    {
        "name": "Low",
        "color": "#3b82f6",  # Blue
        "description": "Low priority task",
        "order_index": 0,
    },
    {
        "name": "Medium",
        "color": "#eab308",  # Yellow
        "description": "Medium priority task",
        "order_index": 1,
    },
    {
        "name": "High",
        "color": "#f97316",  # Orange
        "description": "High priority task",
        "order_index": 2,
    },
    {
        "name": "Urgent",
        "color": "#ef4444",  # Red
        "description": "Urgent priority task",
        "order_index": 3,
    },
]


async def seed_priorities(session: AsyncSession) -> None:
    """Seed default priorities into the database.

    Args:
        session: Database session to use for seeding
    """
    logger.info("Checking for default priorities...")

    for priority_data in DEFAULT_PRIORITIES:
        # Check if priority already exists
        result = await session.execute(
            select(Priority).where(Priority.name == priority_data["name"])
        )
        existing = result.scalar_one_or_none()

        if existing:
            logger.debug(f"Priority '{priority_data['name']}' already exists, skipping")
            continue

        # Create new priority
        priority = Priority(
            id=uuid4(),
            name=priority_data["name"],
            color=priority_data["color"],
            description=priority_data["description"],
            order_index=priority_data["order_index"],
        )
        session.add(priority)
        logger.info(f"Created priority: {priority_data['name']} ({priority_data['color']})")

    await session.commit()
    logger.info("Priority seeding completed")


async def create_inbox_project(session: AsyncSession, user_id: UUID) -> Project:
    """Create the special inbox project for a new user.

    Args:
        session: Database session to use
        user_id: ID of the user to create inbox for

    Returns:
        Created inbox project
    """
    logger.info(f"Creating inbox project for user {user_id}")

    inbox_project = Project(
        id=uuid4(),
        title="Inbox",
        order_index=-1,
        is_inbox=True,
        user_id=user_id,
        parent_id=None
    )
    session.add(inbox_project)
    await session.flush()

    inbox_section = Section(
        title="Inbox",
        project_id=inbox_project.id,
        user_id=user_id
    )
    session.add(inbox_section)
    await session.commit()

    logger.info(f"Created inbox project for user {user_id}")
    return inbox_project


async def seed_database() -> None:
    """Seed all default data into the database."""
    logger.info("Starting database seeding...")

    async with async_session_local() as session:
        try:
            await seed_priorities(session)
            logger.info("Database seeding completed successfully")
        except Exception as e:
            logger.error(f"Error during database seeding: {e}")
            await session.rollback()
            raise
