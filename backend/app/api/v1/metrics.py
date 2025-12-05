"""Custom business metrics endpoint for Prometheus."""

import shutil
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends
from prometheus_client import CollectorRegistry, Gauge, generate_latest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import Response

from ...core.database import get_db
from ...models.media import Anime, Book, Game, Manga, Movie, Show
from ...models.note import Note
from ...models.project import Project
from ...models.task import Task
from ...models.user import User

router = APIRouter()

# Custom Prometheus metrics registry
registry = CollectorRegistry()

# Define custom business metrics
total_users_gauge = Gauge(
    "zero_inertia_total_users",
    "Total number of registered users",
    registry=registry
)

active_users_7d_gauge = Gauge(
    "zero_inertia_active_users_7d",
    "Number of users active in the last 7 days",
    registry=registry
)

active_users_30d_gauge = Gauge(
    "zero_inertia_active_users_30d",
    "Number of users active in the last 30 days",
    registry=registry
)

total_tasks_gauge = Gauge(
    "zero_inertia_total_tasks",
    "Total number of tasks (active, not archived)",
    registry=registry
)

completed_tasks_gauge = Gauge(
    "zero_inertia_completed_tasks",
    "Total number of completed tasks",
    registry=registry
)

total_projects_gauge = Gauge(
    "zero_inertia_total_projects",
    "Total number of projects",
    registry=registry
)

total_notes_gauge = Gauge(
    "zero_inertia_total_notes",
    "Total number of notes",
    registry=registry
)

total_media_gauge = Gauge(
    "zero_inertia_total_media",
    "Total number of media items tracked",
    registry=registry
)

disk_usage_bytes_gauge = Gauge(
    "zero_inertia_disk_usage_bytes",
    "Disk usage in bytes for the application directory",
    registry=registry
)

disk_free_bytes_gauge = Gauge(
    "zero_inertia_disk_free_bytes",
    "Free disk space in bytes",
    registry=registry
)


async def collect_business_metrics(db: AsyncSession) -> None:
    """Collect all business metrics from the database."""
    # Total users
    result = await db.execute(select(func.count(User.id)))
    total_users = result.scalar() or 0
    total_users_gauge.set(total_users)

    # Active users (last 7 days)
    seven_days_ago = datetime.now(UTC) - timedelta(days=7)
    result = await db.execute(
        select(func.count(User.id)).where(User.last_login_at >= seven_days_ago)
    )
    active_7d = result.scalar() or 0
    active_users_7d_gauge.set(active_7d)

    # Active users (last 30 days)
    thirty_days_ago = datetime.now(UTC) - timedelta(days=30)
    result = await db.execute(
        select(func.count(User.id)).where(User.last_login_at >= thirty_days_ago)
    )
    active_30d = result.scalar() or 0
    active_users_30d_gauge.set(active_30d)

    # Total tasks (not archived)
    result = await db.execute(
        select(func.count(Task.id)).where(Task.archived == False)  # noqa: E712
    )
    total_tasks = result.scalar() or 0
    total_tasks_gauge.set(total_tasks)

    # Completed tasks
    result = await db.execute(
        select(func.count(Task.id)).where(
            Task.completed == True,  # noqa: E712
            Task.archived == False  # noqa: E712
        )
    )
    completed_tasks = result.scalar() or 0
    completed_tasks_gauge.set(completed_tasks)

    # Total projects
    result = await db.execute(select(func.count(Project.id)))
    total_projects = result.scalar() or 0
    total_projects_gauge.set(total_projects)

    # Total notes
    result = await db.execute(select(func.count(Note.id)))
    total_notes = result.scalar() or 0
    total_notes_gauge.set(total_notes)

    # Total media items (sum of all media types)
    book_count = (await db.execute(select(func.count(Book.id)))).scalar() or 0
    game_count = (await db.execute(select(func.count(Game.id)))).scalar() or 0
    movie_count = (await db.execute(select(func.count(Movie.id)))).scalar() or 0
    show_count = (await db.execute(select(func.count(Show.id)))).scalar() or 0
    manga_count = (await db.execute(select(func.count(Manga.id)))).scalar() or 0
    anime_count = (await db.execute(select(func.count(Anime.id)))).scalar() or 0
    total_media = book_count + game_count + movie_count + show_count + manga_count + anime_count
    total_media_gauge.set(total_media)

    # Disk usage
    try:
        disk_usage = shutil.disk_usage("/")
        disk_usage_bytes_gauge.set(disk_usage.used)
        disk_free_bytes_gauge.set(disk_usage.free)
    except Exception:
        pass


@router.get("/business-metrics")
async def get_business_metrics(db: AsyncSession = Depends(get_db)):
    """
    Expose custom business metrics in Prometheus format.

    This endpoint is scraped by Prometheus to collect application-specific metrics.
    """
    await collect_business_metrics(db)

    return Response(
        content=generate_latest(registry),
        media_type="text/plain; version=0.0.4"
    )
