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
from app.services import recurring_task_service, streak_service, task_service

DAYS_ARCHIVE_THRESHOLD = 7  # Days after which completed tasks are archived

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


async def archive_old_completed_tasks_job() -> None:
    """
    Background job that archives completed tasks older than a specified number of days.
    """
    logger.info("Running archive old completed tasks job...")

    async for db in get_db():
        try:
            count = await task_service.archive_completed_tasks(db, days=DAYS_ARCHIVE_THRESHOLD)
            logger.info(f"Archived {count} completed tasks older than {DAYS_ARCHIVE_THRESHOLD} days")
        except Exception as e:
            logger.error(f"Error archiving completed tasks: {e}")
        finally:
            await db.close()


async def generate_recurring_tasks_job() -> None:
    """
    Background job that generates tasks from recurring task templates.
    Runs daily at 2:00 AM to create tasks for the current day.
    """
    logger.info("Running generate recurring tasks job...")

    async for db in get_db():
        try:
            count = await recurring_task_service.generate_all_recurring_tasks(db)
            logger.info(f"Generated {count} tasks from recurring task templates")
        except Exception as e:
            logger.error(f"Error generating recurring tasks: {e}")
        finally:
            await db.close()


def setup_scheduler() -> AsyncIOScheduler:
    """
    Initialize and configure the background job scheduler.
    """
    scheduler = AsyncIOScheduler()

    # Run recurring task generation every day at 02:00
    _ = scheduler.add_job(  # pyright: ignore[reportUnknownMemberType]
        generate_recurring_tasks_job,
        trigger=CronTrigger(hour=2, minute=0),
        id="generate_recurring_tasks",
        name="Generate tasks from recurring templates",
        replace_existing=True
    )

    # Run streak reset every day at 02:05 (after recurring tasks)
    _ = scheduler.add_job(  # pyright: ignore[reportUnknownMemberType]
        reset_streaks_job,
        trigger=CronTrigger(hour=2, minute=5),
        id="reset_streaks",
        name="Reset inactive user streaks",
        replace_existing=True
    )

    # Run task archiving every day at 03:00
    _ = scheduler.add_job(  # pyright: ignore[reportUnknownMemberType]
        archive_old_completed_tasks_job,
        trigger=CronTrigger(hour=3, minute=0),
        id="archive_completed_tasks",
        name="Archive old completed tasks",
        replace_existing=True
    )

    logger.info("Scheduler configured with jobs:")
    jobs = cast(list[Job], scheduler.get_jobs())  # pyright: ignore[reportUnknownMemberType]
    for job in jobs:
        logger.info(f"  - {job.name} (ID: {job.id})")  # pyright: ignore[reportUnknownMemberType]

    return scheduler
