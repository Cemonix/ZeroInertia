"""Statistics service for tracking task completion data and analytics."""

from datetime import date, datetime, timedelta, timezone
from typing import cast
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task
from app.schemas.statistics import BestDayInfo, StatisticsSummary


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
