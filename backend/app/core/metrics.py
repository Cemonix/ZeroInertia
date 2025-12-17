from datetime import datetime, timedelta

from prometheus_client import Gauge
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.models.task import Task
from app.models.user import User

# Gauges for current state metrics (values that go up and down)
active_users_gauge = Gauge(
    "zero_inertia_active_users", "Number of users who logged in within the last 24 hours"
)
total_users_gauge = Gauge("zero_inertia_total_users", "Total number of registered users")
total_tasks_gauge = Gauge("zero_inertia_total_tasks", "Total number of tasks created")
total_projects_gauge = Gauge("zero_inertia_total_projects", "Total number of projects created")

# Additional gauges for task metrics
completed_tasks_24h_gauge = Gauge(
    "zero_inertia_completed_tasks_24h", "Number of tasks completed in the last 24 hours"
)


async def update_business_metrics(db: AsyncSession) -> None:
    """
    Updates all business metrics by querying the database.
    This function should be called periodically (e.g., every 30 seconds).
    """
    # Total registered users
    result = await db.execute(select(func.count(User.id)))
    total_users = result.scalar() or 0
    total_users_gauge.set(total_users)

    # Active users (logged in within last 24 hours)
    twenty_four_hours_ago = datetime.now() - timedelta(hours=24)
    result = await db.execute(
        select(func.count(User.id)).where(User.last_login_at >= twenty_four_hours_ago)
    )
    active_users = result.scalar() or 0
    active_users_gauge.set(active_users)

    # Total tasks
    result = await db.execute(select(func.count(Task.id)))
    total_tasks = result.scalar() or 0
    total_tasks_gauge.set(total_tasks)

    # Total projects
    result = await db.execute(select(func.count(Project.id)))
    total_projects = result.scalar() or 0
    total_projects_gauge.set(total_projects)

    # Completed tasks in last 24 hours
    result = await db.execute(
        select(func.count(Task.id)).where(
            Task.completed.is_(True), Task.completed_at >= twenty_four_hours_ago
        )
    )
    completed_tasks_24h = result.scalar() or 0
    completed_tasks_24h_gauge.set(completed_tasks_24h)
