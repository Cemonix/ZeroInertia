from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select

from app.core.logging import logger
from app.models.priority import Priority


async def get_all_priorities(db: AsyncSession) -> Sequence[Priority]:
    """Retrieve all priorities ordered by order_index."""
    logger.debug("Fetching all priorities")
    result = await db.execute(
        select(Priority).order_by(Priority.order_index)
    )
    priorities = result.scalars().all()
    logger.debug(f"Found {len(priorities)} priorities")
    return priorities
