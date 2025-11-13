"""Pydantic schemas for statistics and calendar data."""

from datetime import date
from typing import ClassVar

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
