"""
Background job scheduler using APScheduler.
Handles recurring tasks like resetting inactive streaks at midnight.
"""
from datetime import datetime, timedelta, timezone
from typing import cast

from apscheduler.job import Job
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import and_, select

from app.core.database import get_db
from app.core.logging import logger
from app.core.metrics import update_business_metrics
from app.models.task import Task
from app.services import notification_service, streak_service, task_service

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


async def update_metrics_job() -> None:
    """
    Background job that updates Prometheus business metrics.
    Runs every 30 seconds to keep metrics current.
    """
    async for db in get_db():
        try:
            await update_business_metrics(db)
        except Exception as e:
            logger.error(f"Failed to update metrics: {e}")
        finally:
            await db.close()


async def send_task_reminders_job() -> None:
    """
    Background job that checks for tasks with reminders and sends push notifications.
    Runs every 5 minutes. Only sends notifications for tasks that have reminder_minutes set.

    Logic: For each task with a reminder, check if current time is within the reminder window.
    Reminder window = (due_datetime - reminder_minutes) ± 5 minutes tolerance.
    """
    logger.info("Running task reminders job...")

    async for db in get_db():
        try:
            now = datetime.now(timezone.utc)
            notification_count = 0

            # Query all tasks that:
            # 1. Have a due_datetime set
            # 2. Have reminder_minutes set (not null)
            # 3. Are not completed or archived
            result = await db.execute(
                select(Task).where(
                    and_(
                        Task.due_datetime.isnot(None),
                        Task.reminder_minutes.isnot(None),
                        Task.completed.is_(False),
                        Task.archived.is_(False),
                    )
                )
            )
            tasks = result.scalars().all()

            for task in tasks:
                if task.due_datetime is None or task.reminder_minutes is None:
                    continue  # Skip tasks without due date or reminder

                # Calculate when the reminder should fire
                # reminder_time = due_datetime - reminder_minutes
                reminder_time = task.due_datetime - timedelta(minutes=task.reminder_minutes)

                # Check if we're within the reminder window (±5 minutes tolerance)
                # This gives a 10-minute window since job runs every 5 minutes
                time_diff = abs((now - reminder_time).total_seconds() / 60)

                if time_diff <= 5:
                    # Format due time for notification message
                    minutes_until_due = int((task.due_datetime - now).total_seconds() / 60)

                    if minutes_until_due <= 0:
                        time_str = "now"
                    elif minutes_until_due < 60:
                        time_str = f"in {minutes_until_due} minutes"
                    elif minutes_until_due < 1440:
                        hours = minutes_until_due // 60
                        time_str = f"in {hours} hour{'s' if hours > 1 else ''}"
                    else:
                        days = minutes_until_due // 1440
                        time_str = f"in {days} day{'s' if days > 1 else ''}"

                    try:
                        count = await notification_service.send_task_reminder(
                            db=db,
                            user_id=task.user_id,
                            task_title=task.title,
                            task_id=task.id,
                            due_datetime=time_str,
                        )
                        notification_count += count
                        logger.debug(
                            f"Sent reminder for task '{task.title}' (ID: {task.id}) " +
                            f"with {task.reminder_minutes}min reminder, due {time_str}"
                        )
                    except Exception as e:
                        logger.error(f"Error sending reminder for task {task.id}: {e}")

            if notification_count > 0:
                logger.info(f"Sent {notification_count} task reminder notifications")
            else:
                logger.debug("No task reminders to send in this cycle")

        except Exception as e:
            logger.error(f"Error in task reminders job: {e}")
        finally:
            await db.close()


def setup_scheduler() -> AsyncIOScheduler:
    """
    Initialize and configure the background job scheduler.
    """
    scheduler = AsyncIOScheduler()

    # Run streak reset every day at 02:00
    _ = scheduler.add_job(
        reset_streaks_job,
        trigger=CronTrigger(hour=2, minute=0),
        id="reset_streaks",
        name="Reset inactive user streaks",
        replace_existing=True
    )

    # Run task archiving every day at 03:00
    _ = scheduler.add_job(
        archive_old_completed_tasks_job,
        trigger=CronTrigger(hour=3, minute=0),
        id="archive_completed_tasks",
        name="Archive old completed tasks",
        replace_existing=True
    )

    # Run task reminders every 5 minutes
    _ = scheduler.add_job(
        send_task_reminders_job,
        trigger=IntervalTrigger(minutes=5),
        id="send_task_reminders",
        name="Send task reminder notifications",
        replace_existing=True
    )

    # Update Prometheus metrics every 30 seconds
    _ = scheduler.add_job(
        update_metrics_job,
        trigger=IntervalTrigger(seconds=30),
        id="update_business_metrics",
        name="Update Prometheus business metrics",
        replace_existing=True
    )

    logger.info("Scheduler configured with jobs:")
    jobs = cast(list[Job], scheduler.get_jobs())
    for job in jobs:
        logger.info(f"  - {job.name} (ID: {job.id})")

    return scheduler
