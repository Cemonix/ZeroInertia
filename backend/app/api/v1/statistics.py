"""API endpoints for task completion statistics and calendar data."""

from datetime import date, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth_deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.statistics import (
    CalendarHeatmapData,
    CompletionStatistics,
    DailyCompletionData,
)
from app.services import statistics_service

router = APIRouter()


@router.get("/daily", response_model=DailyCompletionData)
async def get_daily_completions(
    start_date: Annotated[
        date,
        Query(description="Start date for the range (YYYY-MM-DD)", examples=["2025-01-01"]),
    ],
    end_date: Annotated[
        date,
        Query(description="End date for the range (YYYY-MM-DD)", examples=["2025-01-31"]),
    ],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DailyCompletionData:
    """
    Get daily task completion counts for a date range.

    Returns completion counts for each day in the specified range.
    Useful for custom date range visualizations.

    Args:
        start_date: Start date (inclusive)
        end_date: End date (inclusive)
        db: Database session
        current_user: Authenticated user

    Returns:
        DailyCompletionData with date->count mapping and metadata
    """
    daily_counts = await statistics_service.get_daily_completion_counts(
        db, current_user.id, start_date, end_date
    )

    total_completions = sum(daily_counts.values())

    return DailyCompletionData(
        daily_counts=daily_counts,
        start_date=start_date,
        end_date=end_date,
        total_completions=total_completions,
    )


@router.get("/calendar/{year}", response_model=CalendarHeatmapData)
async def get_calendar_heatmap(
    year: Annotated[
        int,
        Path(description="Year for the calendar (e.g., 2025)", ge=2000, le=2100),
    ],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CalendarHeatmapData:
    """
    Get year-long completion data for GitHub-style calendar heatmap.

    Returns completion counts for every day in the specified year,
    optimized for rendering an annual contribution graph.

    Args:
        year: Year to get calendar data for
        db: Database session
        current_user: Authenticated user

    Returns:
        CalendarHeatmapData with full year of daily counts
    """
    daily_counts = await statistics_service.get_calendar_heatmap_data(
        db, current_user.id, year
    )

    total_completions = sum(daily_counts.values())
    max_day_count = max(daily_counts.values()) if daily_counts else 0

    return CalendarHeatmapData(
        year=year,
        daily_counts=daily_counts,
        total_completions=total_completions,
        max_day_count=max_day_count,
    )


@router.get("/calendar", response_model=CalendarHeatmapData)
async def get_current_year_calendar(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CalendarHeatmapData:
    """
    Get current year's completion data for GitHub-style calendar heatmap.

    Convenience endpoint that returns calendar data for the current year.

    Args:
        db: Database session
        current_user: Authenticated user

    Returns:
        CalendarHeatmapData with full year of daily counts
    """
    current_year = datetime.now().year
    daily_counts = await statistics_service.get_calendar_heatmap_data(
        db, current_user.id, current_year
    )

    total_completions = sum(daily_counts.values())
    max_day_count = max(daily_counts.values()) if daily_counts else 0

    return CalendarHeatmapData(
        year=current_year,
        daily_counts=daily_counts,
        total_completions=total_completions,
        max_day_count=max_day_count,
    )


@router.get("/summary", response_model=CompletionStatistics)
async def get_completion_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CompletionStatistics:
    """
    Get overall completion statistics and insights.

    Returns various statistics about task completion patterns including
    totals, recent activity, averages, and best day.

    Args:
        db: Database session
        current_user: Authenticated user

    Returns:
        CompletionStatistics with various metrics
    """
    # Get general statistics
    stats = await statistics_service.get_completion_statistics(db, current_user.id)

    # Get best day statistics
    best_day = await statistics_service.get_best_day_statistics(db, current_user.id)

    return CompletionStatistics(
        total_completed=stats.total_completed,
        completed_today=stats.completed_today,
        completed_this_week=stats.completed_this_week,
        completed_this_month=stats.completed_this_month,
        average_per_day=stats.average_per_day,
        best_day_count=best_day.best_day_count,
        best_day_date=best_day.best_day_date,
    )
