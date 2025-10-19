"""
Background job scheduler using APScheduler.
Handles recurring tasks like resetting inactive streaks at midnight.
"""
from typing import cast

from apscheduler.job import Job
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.database import get_db
from app.core.logging import logger
from app.services import streak_service


async def reset_streaks_job() -> None:
    """
    Background job that runs at midnight to reset streaks for inactive users.
    """
    logger.info("Running midnight streak reset job...")

    async for db in get_db():
        try:
            count = await streak_service.reset_inactive_streaks(db)
            logger.info(f"Reset {count} inactive streaks")
        except Exception as e:
            logger.error(f"Error resetting streaks: {e}")
        finally:
            await db.close()


def setup_scheduler() -> AsyncIOScheduler:
    """
    Initialize and configure the background job scheduler.
    """
    scheduler = AsyncIOScheduler()

    # Run streak reset every day at 02:00
    _ = scheduler.add_job(  # pyright: ignore[reportUnknownMemberType]
        reset_streaks_job,
        trigger=CronTrigger(hour=2, minute=0),
        id="reset_streaks",
        name="Reset inactive user streaks",
        replace_existing=True
    )

    logger.info("Scheduler configured with jobs:")
    jobs = cast(list[Job], scheduler.get_jobs())  # pyright: ignore[reportUnknownMemberType]
    for job in jobs:
        logger.info(f"  - {job.name} (ID: {job.id})")  # pyright: ignore[reportUnknownMemberType]

    return scheduler
