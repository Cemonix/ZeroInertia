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
    DistributionResponse,
    ProductivityPatternsResponse,
    ProjectStatisticsResponse,
    TrendsResponse,
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


@router.get("/projects", response_model=ProjectStatisticsResponse)
async def get_project_statistics(
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
) -> ProjectStatisticsResponse:
    """
    Get project-level completion statistics for a date range.

    Returns statistics showing which projects had the most task completions
    in the specified period. Useful for identifying productive projects
    and projects that need attention.

    Args:
        start_date: Start date (inclusive)
        end_date: End date (inclusive)
        db: Database session
        current_user: Authenticated user

    Returns:
        ProjectStatisticsResponse with project completion data
    """
    project_stats = await statistics_service.get_project_statistics(
        db, current_user.id, start_date, end_date
    )

    total_completed = sum(p.completed_count for p in project_stats)

    return ProjectStatisticsResponse(
        projects=project_stats,
        total_completed=total_completed,
        start_date=start_date,
        end_date=end_date,
    )


@router.get("/patterns", response_model=ProductivityPatternsResponse)
async def get_productivity_patterns(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProductivityPatternsResponse:
    """
    Get productivity patterns by day of week.

    Returns statistics showing which days of the week the user is most
    productive (all-time). Helps identify patterns and optimize scheduling.

    Args:
        db: Database session
        current_user: Authenticated user

    Returns:
        ProductivityPatternsResponse with day-of-week statistics
    """
    day_stats = await statistics_service.get_day_of_week_patterns(
        db, current_user.id
    )

    most_productive = max(day_stats, key=lambda x: x.completed_count)
    least_productive = min(day_stats, key=lambda x: x.completed_count)

    return ProductivityPatternsResponse(
        by_day_of_week=day_stats,
        most_productive_day=most_productive.day_name,
        least_productive_day=least_productive.day_name,
    )


@router.get("/trends", response_model=TrendsResponse)
async def get_completion_trends(
    period_type: Annotated[
        str,
        Query(
            description="Period type for trends",
            pattern="^(week|month)$",
            examples=["week"],
        ),
    ] = "week",
    num_periods: Annotated[
        int,
        Query(
            description="Number of periods to include",
            ge=1,
            le=52,
            examples=[8],
        ),
    ] = 8,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TrendsResponse:
    """
    Get completion trends over time.

    Returns completion counts for the last N weeks or months,
    along with trend direction analysis.

    Args:
        period_type: "week" or "month"
        num_periods: Number of periods to include (1-52)
        db: Database session
        current_user: Authenticated user

    Returns:
        TrendsResponse with period data and trend analysis
    """
    periods = await statistics_service.get_completion_trends(
        db, current_user.id, period_type, num_periods
    )

    if len(periods) < 2:
        trend_direction = "stable"
        average_change_percent = 0.0
    else:
        changes: list[float] = []
        for i in range(1, len(periods)):
            prev_count = periods[i - 1].completed_count
            curr_count = periods[i].completed_count

            if prev_count == 0:
                if curr_count > 0:
                    changes.append(100.0)
            else:
                change_percent = ((curr_count - prev_count) / prev_count) * 100
                changes.append(change_percent)

        average_change_percent = (
            sum(changes) / len(changes) if changes else 0.0
        )

        if average_change_percent > 5.0:
            trend_direction = "up"
        elif average_change_percent < -5.0:
            trend_direction = "down"
        else:
            trend_direction = "stable"

    return TrendsResponse(
        periods=periods,
        trend_direction=trend_direction,
        average_change_percent=round(average_change_percent, 2),
    )


@router.get("/distribution", response_model=DistributionResponse)
async def get_distribution_statistics(
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
) -> DistributionResponse:
    """
    Get distribution of completions by priority and labels.

    Returns statistics showing how completed tasks are distributed across
    priority levels and labels. Useful for understanding work patterns.

    Args:
        start_date: Start date (inclusive)
        end_date: End date (inclusive)
        db: Database session
        current_user: Authenticated user

    Returns:
        DistributionResponse with priority and label distributions
    """
    priority_dist = await statistics_service.get_priority_distribution(
        db, current_user.id, start_date, end_date
    )

    label_dist = await statistics_service.get_label_distribution(
        db, current_user.id, start_date, end_date, limit=10
    )

    total_completed = sum(p.completed_count for p in priority_dist)

    return DistributionResponse(
        by_priority=priority_dist,
        by_labels=label_dist,
        total_completed=total_completed,
    )
