"""Pydantic schemas for statistics and calendar data."""

from datetime import date
from typing import ClassVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DailyCompletionData(BaseModel):
    """Schema for daily task completion counts."""

    daily_counts: dict[str, int] = Field(
        ...,
        description="Dictionary mapping date strings (YYYY-MM-DD) to completion counts",
        examples=[{"2025-01-15": 5, "2025-01-16": 3, "2025-01-17": 0}],
    )
    start_date: date = Field(..., description="Start date of the range")
    end_date: date = Field(..., description="End date of the range")
    total_completions: int = Field(
        ..., description="Total completions in the date range"
    )


class CalendarHeatmapData(BaseModel):
    """Schema for GitHub-style calendar heatmap data."""

    year: int = Field(..., description="Year of the calendar data", examples=[2025])
    daily_counts: dict[str, int] = Field(
        ...,
        description="Dictionary with all dates in year and their completion counts",
        examples=[{"2025-01-01": 0, "2025-01-02": 3, "2025-01-03": 5}],
    )
    total_completions: int = Field(
        ..., description="Total completions for the year"
    )
    max_day_count: int = Field(
        ..., description="Maximum completions in a single day"
    )


class CompletionStatistics(BaseModel):
    """Schema for overall completion statistics."""

    total_completed: int = Field(
        ..., description="Total number of completed tasks all-time"
    )
    completed_today: int = Field(..., description="Tasks completed today")
    completed_this_week: int = Field(
        ..., description="Tasks completed in the last 7 days"
    )
    completed_this_month: int = Field(
        ..., description="Tasks completed in the last 30 days"
    )
    average_per_day: float = Field(
        ..., description="Average completions per day (last 30 days)"
    )
    best_day_count: int = Field(
        ..., description="Maximum tasks completed in a single day (all-time)"
    )
    best_day_date: str | None = Field(
        ..., description="Date of most productive day (YYYY-MM-DD format or null)"
    )


class DateRangeQuery(BaseModel):
    """Schema for date range query parameters."""

    start_date: date = Field(..., description="Start date (inclusive)")
    end_date: date = Field(..., description="End date (inclusive)")

    model_config: ClassVar[ConfigDict] = ConfigDict(
        json_schema_extra={
            "example": {
                "start_date": "2025-01-01",
                "end_date": "2025-01-31",
            }
        }
    )


class StatisticsSummary(BaseModel):
    """Internal schema for general statistics summary."""

    total_completed: int
    completed_today: int
    completed_this_week: int
    completed_this_month: int
    average_per_day: float


class BestDayInfo(BaseModel):
    """Internal schema for best day statistics."""

    best_day_count: int
    best_day_date: str | None


class ProjectStatistics(BaseModel):
    """Statistics for a single project."""

    project_id: UUID = Field(..., description="Project UUID")
    project_title: str = Field(..., description="Project name")
    completed_count: int = Field(
        ..., description="Number of completed tasks in this project"
    )
    completion_percentage: float = Field(
        ..., description="Percentage of total completions in the period"
    )


class ProjectStatisticsResponse(BaseModel):
    """Project-level statistics for a date range."""

    projects: list[ProjectStatistics] = Field(
        ..., description="List of project statistics ordered by completion count"
    )
    total_completed: int = Field(
        ..., description="Total completions across all projects in the period"
    )
    start_date: date = Field(..., description="Start of the date range")
    end_date: date = Field(..., description="End of the date range")


class DayOfWeekStatistics(BaseModel):
    """Completion patterns by day of week."""

    day_of_week: int = Field(
        ..., description="Day of week (0=Monday, 6=Sunday)", ge=0, le=6
    )
    day_name: str = Field(..., description="Name of the day (e.g., 'Monday')")
    completed_count: int = Field(
        ..., description="Total completions on this day of week (all-time)"
    )
    average_per_week: float = Field(
        ..., description="Average completions per week on this day"
    )


class ProductivityPatternsResponse(BaseModel):
    """Weekly productivity patterns."""

    by_day_of_week: list[DayOfWeekStatistics] = Field(
        ..., description="Statistics for each day of the week"
    )
    most_productive_day: str = Field(
        ..., description="Name of the most productive day"
    )
    least_productive_day: str = Field(
        ..., description="Name of the least productive day"
    )


class TrendPeriod(BaseModel):
    """Statistics for a single period (week/month)."""

    period_start: date = Field(..., description="Start date of the period")
    period_end: date = Field(..., description="End date of the period")
    completed_count: int = Field(..., description="Completions in this period")


class TrendsResponse(BaseModel):
    """Week-over-week or month-over-month trends."""

    periods: list[TrendPeriod] = Field(
        ..., description="List of periods with their completion counts"
    )
    trend_direction: str = Field(
        ..., description="Overall trend direction: 'up', 'down', or 'stable'"
    )
    average_change_percent: float = Field(
        ..., description="Average percentage change between periods"
    )


class PriorityDistribution(BaseModel):
    """Task completions by priority level."""

    priority_id: UUID | None = Field(..., description="Priority UUID or null for none")
    priority_name: str = Field(..., description="Priority name (e.g., 'High', 'None')")
    completed_count: int = Field(
        ..., description="Number of completed tasks with this priority"
    )
    percentage: float = Field(
        ..., description="Percentage of total completions"
    )


class LabelDistribution(BaseModel):
    """Task completions by label."""

    label_id: UUID = Field(..., description="Label UUID")
    label_name: str = Field(..., description="Label name")
    label_color: str = Field(..., description="Label color (hex code)")
    completed_count: int = Field(
        ..., description="Number of completed tasks with this label"
    )
    percentage: float = Field(
        ..., description="Percentage of total completions"
    )


class DistributionResponse(BaseModel):
    """Distribution of completions by priority and labels."""

    by_priority: list[PriorityDistribution] = Field(
        ..., description="Distribution by priority levels"
    )
    by_labels: list[LabelDistribution] = Field(
        ..., description="Distribution by labels (top 10)"
    )
    total_completed: int = Field(
        ..., description="Total completions in the period"
    )
