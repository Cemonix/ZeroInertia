"""Statistics service for tracking task completion data and analytics."""

from datetime import date, datetime, timedelta, timezone
from typing import cast
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.label import Label, task_labels
from app.models.priority import Priority
from app.models.project import Project
from app.models.task import Task
from app.schemas.statistics import (
    BestDayInfo,
    DayOfWeekStatistics,
    LabelDistribution,
    PriorityDistribution,
    ProjectStatistics,
    StatisticsSummary,
    TrendPeriod,
)


async def get_daily_completion_counts(
    db: AsyncSession,
    user_id: UUID,
    start_date: date,
    end_date: date,
) -> dict[str, int]:
    """
    Get task completion counts grouped by date for a date range.

    Returns a dictionary mapping date strings (YYYY-MM-DD) to completion counts.
    Dates with no completions will not be included in the result.

    Args:
        db: Database session
        user_id: User ID to filter tasks
        start_date: Start date for the range (inclusive)
        end_date: End date for the range (inclusive)

    Returns:
        Dictionary with date strings as keys and completion counts as values
        Example: {"2025-01-15": 5, "2025-01-16": 3}
    """
    # Convert dates to datetime with timezone for comparison
    start_datetime = datetime.combine(start_date, datetime.min.time()).replace(
        tzinfo=timezone.utc
    )
    end_datetime = datetime.combine(
        end_date, datetime.max.time()
    ).replace(tzinfo=timezone.utc)

    # Query to group completed tasks by date
    # Cast completed_at to date and count tasks per day
    stmt = (
        select(
            func.date(Task.completed_at).label("completion_date"),
            func.count(Task.id).label("count"),
        )
        .where(
            Task.user_id == user_id,
            Task.completed.is_(True),
            Task.completed_at.isnot(None),
            Task.completed_at >= start_datetime,
            Task.completed_at <= end_datetime,
        )
        .group_by(func.date(Task.completed_at))
        .order_by(func.date(Task.completed_at))
    )

    result = await db.execute(stmt)
    rows = result.all()

    # Convert to dictionary with string keys
    completion_dict: dict[str, int] = {}
    for row in rows:
        if not row[0] or not row[1]:
            continue

        completion_date = cast(date, row[0])
        count_value = cast(int, row[1])
        completion_dict[completion_date.isoformat()] = count_value
    return completion_dict


async def get_completion_statistics(
    db: AsyncSession,
    user_id: UUID,
) -> StatisticsSummary:
    """
    Get overall completion statistics for a user.

    Returns various statistics about task completion patterns.

    Args:
        db: Database session
        user_id: User ID to get statistics for

    Returns:
        StatisticsSummary with completion metrics
    """
    now = datetime.now(timezone.utc)
    today_start = datetime.combine(now.date(), datetime.min.time()).replace(
        tzinfo=timezone.utc
    )
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    # Total completed tasks
    total_stmt = select(func.count(Task.id)).where(
        Task.user_id == user_id,
        Task.completed.is_(True),
    )
    total_result = await db.execute(total_stmt)
    total_completed = total_result.scalar() or 0

    # Completed today
    today_stmt = select(func.count(Task.id)).where(
        Task.user_id == user_id,
        Task.completed.is_(True),
        Task.completed_at.isnot(None),
        Task.completed_at >= today_start,
    )
    today_result = await db.execute(today_stmt)
    completed_today = today_result.scalar() or 0

    # Completed this week (last 7 days)
    week_stmt = select(func.count(Task.id)).where(
        Task.user_id == user_id,
        Task.completed.is_(True),
        Task.completed_at.isnot(None),
        Task.completed_at >= week_ago,
    )
    week_result = await db.execute(week_stmt)
    completed_this_week = week_result.scalar() or 0

    # Completed this month (last 30 days)
    month_stmt = select(func.count(Task.id)).where(
        Task.user_id == user_id,
        Task.completed.is_(True),
        Task.completed_at.isnot(None),
        Task.completed_at >= month_ago,
    )
    month_result = await db.execute(month_stmt)
    completed_this_month = month_result.scalar() or 0

    # Calculate average per day (last 30 days)
    average_per_day = completed_this_month / 30.0 if completed_this_month > 0 else 0.0

    return StatisticsSummary(
        total_completed=total_completed,
        completed_today=completed_today,
        completed_this_week=completed_this_week,
        completed_this_month=completed_this_month,
        average_per_day=round(average_per_day, 2),
    )


async def get_calendar_heatmap_data(
    db: AsyncSession,
    user_id: UUID,
    year: int,
) -> dict[str, int]:
    """
    Get year-long completion data optimized for GitHub-style calendar heatmap.

    Returns completion counts for every day in the specified year.
    This is optimized for rendering an annual contribution graph.

    Args:
        db: Database session
        user_id: User ID to filter tasks
        year: Year to get data for (e.g., 2025)

    Returns:
        Dictionary with date strings as keys and completion counts as values
        Example: {"2025-01-01": 0, "2025-01-02": 3, ...}
    """
    start_date = date(year, 1, 1)
    end_date = date(year, 12, 31)

    # Get completion counts for the year
    daily_counts = await get_daily_completion_counts(
        db, user_id, start_date, end_date
    )

    # Fill in missing dates with 0 counts for complete year visualization
    result: dict[str, int] = {}
    current_date = start_date

    while current_date <= end_date:
        date_str = current_date.isoformat()
        result[date_str] = daily_counts.get(date_str) or 0
        current_date += timedelta(days=1)

    return result


async def get_best_day_statistics(
    db: AsyncSession,
    user_id: UUID,
) -> BestDayInfo:
    """
    Get statistics about the user's most productive day.

    Args:
        db: Database session
        user_id: User ID to get statistics for

    Returns:
        BestDayInfo with best day count and date
    """
    # Find the day with most completions
    stmt = (
        select(
            func.date(Task.completed_at).label("completion_date"),
            func.count(Task.id).label("count"),
        )
        .where(
            Task.user_id == user_id,
            Task.completed.is_(True),
            Task.completed_at.isnot(None),
        )
        .group_by(func.date(Task.completed_at))
        .order_by(func.count(Task.id).desc())
        .limit(1)
    )

    result = await db.execute(stmt)
    row = result.first()

    if row:
        if not row[0] or not row[1]:
            return BestDayInfo(
                best_day_count=0,
                best_day_date=None,
            )

        completion_date = cast(date, row[0])
        count_value = cast(int, row[1])
        return BestDayInfo(
            best_day_count=count_value,
            best_day_date=completion_date.isoformat(),
        )

    return BestDayInfo(
        best_day_count=0,
        best_day_date=None,
    )


async def get_project_statistics(
    db: AsyncSession,
    user_id: UUID,
    start_date: date,
    end_date: date,
) -> list[ProjectStatistics]:
    """
    Get completion counts grouped by project for a date range.

    Returns projects ordered by completion count (descending).

    Args:
        db: Database session
        user_id: User ID to filter tasks
        start_date: Start date for the range (inclusive)
        end_date: End date for the range (inclusive)

    Returns:
        List of ProjectStatistics ordered by completed_count desc
    """
    start_datetime = datetime.combine(start_date, datetime.min.time()).replace(
        tzinfo=timezone.utc
    )
    end_datetime = datetime.combine(end_date, datetime.max.time()).replace(
        tzinfo=timezone.utc
    )

    stmt = (
        select(
            Project.id,
            Project.title,
            func.count(Task.id).label("completed_count"),
        )
        .join(Task, Task.project_id == Project.id)
        .where(
            Task.user_id == user_id,
            Task.completed.is_(True),
            Task.completed_at.isnot(None),
            Task.completed_at >= start_datetime,
            Task.completed_at <= end_datetime,
        )
        .group_by(Project.id, Project.title)
        .order_by(func.count(Task.id).desc())
    )

    result = await db.execute(stmt)
    rows = result.all()

    total_completed = sum(row[2] for row in rows)

    project_stats: list[ProjectStatistics] = []
    for row in rows:
        project_id = cast(UUID, row[0])
        project_title = cast(str, row[1])
        completed_count = cast(int, row[2])
        completion_percentage = (
            (completed_count / total_completed * 100) if total_completed > 0 else 0.0
        )

        project_stats.append(
            ProjectStatistics(
                project_id=project_id,
                project_title=project_title,
                completed_count=completed_count,
                completion_percentage=round(completion_percentage, 2),
            )
        )

    return project_stats


async def get_day_of_week_patterns(
    db: AsyncSession,
    user_id: UUID,
) -> list[DayOfWeekStatistics]:
    """
    Get completion patterns by day of week (all-time).

    Returns statistics for each day of the week (Monday=0 to Sunday=6).

    Args:
        db: Database session
        user_id: User ID to get statistics for

    Returns:
        List of DayOfWeekStatistics for each day of the week
    """
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    stmt = (
        select(
            func.extract("dow", Task.completed_at).label("day_of_week"),
            func.count(Task.id).label("count"),
        )
        .where(
            Task.user_id == user_id,
            Task.completed.is_(True),
            Task.completed_at.isnot(None),
        )
        .group_by(func.extract("dow", Task.completed_at))
    )

    result = await db.execute(stmt)
    rows = result.all()

    dow_counts: dict[int, int] = {}
    for row in rows:
        dow_postgres = cast(int, row[0])
        count = cast(int, row[1])
        dow_monday_zero = (dow_postgres + 6) % 7
        dow_counts[dow_monday_zero] = count

    first_completion_stmt = (
        select(func.min(Task.completed_at))
        .where(
            Task.user_id == user_id,
            Task.completed.is_(True),
            Task.completed_at.isnot(None),
        )
    )
    first_completion_result = await db.execute(first_completion_stmt)
    first_completion = first_completion_result.scalar()

    weeks_elapsed = 1.0
    if first_completion:
        now = datetime.now(timezone.utc)
        days_elapsed = (now - first_completion).days
        weeks_elapsed = max(days_elapsed / 7.0, 1.0)

    day_stats: list[DayOfWeekStatistics] = []
    for dow in range(7):
        count = dow_counts.get(dow, 0)
        avg_per_week = count / weeks_elapsed

        day_stats.append(
            DayOfWeekStatistics(
                day_of_week=dow,
                day_name=day_names[dow],
                completed_count=count,
                average_per_week=round(avg_per_week, 2),
            )
        )

    return day_stats


async def get_completion_trends(
    db: AsyncSession,
    user_id: UUID,
    period_type: str,
    num_periods: int = 8,
) -> list[TrendPeriod]:
    """
    Get completion trends over last N weeks or months.

    Args:
        db: Database session
        user_id: User ID to get trends for
        period_type: "week" or "month"
        num_periods: Number of periods to include (default 8)

    Returns:
        List of TrendPeriod objects ordered chronologically
    """
    now = datetime.now(timezone.utc)
    periods: list[TrendPeriod] = []

    for i in range(num_periods - 1, -1, -1):
        if period_type == "week":
            period_end = (now - timedelta(weeks=i)).date()
            period_start = period_end - timedelta(days=6)
        else:
            period_end = (now - timedelta(days=i * 30)).date()
            period_start = period_end - timedelta(days=29)

        start_datetime = datetime.combine(period_start, datetime.min.time()).replace(
            tzinfo=timezone.utc
        )
        end_datetime = datetime.combine(period_end, datetime.max.time()).replace(
            tzinfo=timezone.utc
        )

        stmt = select(func.count(Task.id)).where(
            Task.user_id == user_id,
            Task.completed.is_(True),
            Task.completed_at.isnot(None),
            Task.completed_at >= start_datetime,
            Task.completed_at <= end_datetime,
        )

        result = await db.execute(stmt)
        count = result.scalar() or 0

        periods.append(
            TrendPeriod(
                period_start=period_start,
                period_end=period_end,
                completed_count=count,
            )
        )

    return periods


async def get_priority_distribution(
    db: AsyncSession,
    user_id: UUID,
    start_date: date,
    end_date: date,
) -> list[PriorityDistribution]:
    """
    Get completion distribution by priority level for a date range.

    Args:
        db: Database session
        user_id: User ID to filter tasks
        start_date: Start date for the range (inclusive)
        end_date: End date for the range (inclusive)

    Returns:
        List of PriorityDistribution ordered by completed_count desc
    """
    start_datetime = datetime.combine(start_date, datetime.min.time()).replace(
        tzinfo=timezone.utc
    )
    end_datetime = datetime.combine(end_date, datetime.max.time()).replace(
        tzinfo=timezone.utc
    )

    stmt = (
        select(
            Priority.id,
            Priority.name,
            func.count(Task.id).label("completed_count"),
        )
        .outerjoin(Task, Task.priority_id == Priority.id)
        .where(
            Task.user_id == user_id,
            Task.completed.is_(True),
            Task.completed_at.isnot(None),
            Task.completed_at >= start_datetime,
            Task.completed_at <= end_datetime,
        )
        .group_by(Priority.id, Priority.name)
        .order_by(func.count(Task.id).desc())
    )

    result = await db.execute(stmt)
    rows = result.all()

    none_priority_stmt = select(func.count(Task.id)).where(
        Task.user_id == user_id,
        Task.completed.is_(True),
        Task.completed_at.isnot(None),
        Task.completed_at >= start_datetime,
        Task.completed_at <= end_datetime,
        Task.priority_id.is_(None),
    )
    none_result = await db.execute(none_priority_stmt)
    none_count = none_result.scalar() or 0

    total_completed = sum(row[2] for row in rows) + none_count

    distributions: list[PriorityDistribution] = []

    for row in rows:
        priority_id = cast(UUID, row[0])
        priority_name = cast(str, row[1])
        completed_count = cast(int, row[2])
        percentage = (
            (completed_count / total_completed * 100) if total_completed > 0 else 0.0
        )

        distributions.append(
            PriorityDistribution(
                priority_id=priority_id,
                priority_name=priority_name,
                completed_count=completed_count,
                percentage=round(percentage, 2),
            )
        )

    if none_count > 0:
        percentage = (none_count / total_completed * 100) if total_completed > 0 else 0.0
        distributions.append(
            PriorityDistribution(
                priority_id=None,
                priority_name="None",
                completed_count=none_count,
                percentage=round(percentage, 2),
            )
        )

    distributions.sort(key=lambda x: x.completed_count, reverse=True)

    return distributions


async def get_label_distribution(
    db: AsyncSession,
    user_id: UUID,
    start_date: date,
    end_date: date,
    limit: int = 10,
) -> list[LabelDistribution]:
    """
    Get top N labels by completion count for a date range.

    Args:
        db: Database session
        user_id: User ID to filter tasks
        start_date: Start date for the range (inclusive)
        end_date: End date for the range (inclusive)
        limit: Maximum number of labels to return (default 10)

    Returns:
        List of LabelDistribution ordered by completed_count desc (top N)
    """
    start_datetime = datetime.combine(start_date, datetime.min.time()).replace(
        tzinfo=timezone.utc
    )
    end_datetime = datetime.combine(end_date, datetime.max.time()).replace(
        tzinfo=timezone.utc
    )

    stmt = (
        select(
            Label.id,
            Label.name,
            Label.color,
            func.count(Task.id).label("completed_count"),
        )
        .join(task_labels, task_labels.c.label_id == Label.id)
        .join(Task, Task.id == task_labels.c.task_id)
        .where(
            Task.user_id == user_id,
            Task.completed.is_(True),
            Task.completed_at.isnot(None),
            Task.completed_at >= start_datetime,
            Task.completed_at <= end_datetime,
        )
        .group_by(Label.id, Label.name, Label.color)
        .order_by(func.count(Task.id).desc())
        .limit(limit)
    )

    result = await db.execute(stmt)
    rows = result.all()

    total_stmt = select(func.count(Task.id)).where(
        Task.user_id == user_id,
        Task.completed.is_(True),
        Task.completed_at.isnot(None),
        Task.completed_at >= start_datetime,
        Task.completed_at <= end_datetime,
    )
    total_result = await db.execute(total_stmt)
    total_completed = total_result.scalar() or 0

    distributions: list[LabelDistribution] = []
    for row in rows:
        label_id = cast(UUID, row[0])
        label_name = cast(str, row[1])
        label_color = cast(str | None, row[2]) or "#808080"
        completed_count = cast(int, row[3])
        percentage = (
            (completed_count / total_completed * 100) if total_completed > 0 else 0.0
        )

        distributions.append(
            LabelDistribution(
                label_id=label_id,
                label_name=label_name,
                label_color=label_color,
                completed_count=completed_count,
                percentage=round(percentage, 2),
            )
        )

    return distributions
