from datetime import datetime
from typing import ClassVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.label import LabelResponse


class TaskCreate(BaseModel):
    """Schema for creating a task"""
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    project_id: UUID | None = None
    section_id: UUID | None = None
    priority_id: UUID | None = None
    due_datetime: datetime | None = None
    reminder_minutes: int | None = None  # Minutes before due_datetime to send notification
    duration_minutes: int | None = None  # Estimated time to complete task in minutes
    recurrence_interval: int | None = None  # How many units between occurrences
    recurrence_unit: str | None = None  # days | weeks | months | years
    recurrence_days: list[int] | None = None  # For weekly: 0=Mon, 6=Sun (Python weekday convention)
    label_ids: list[UUID] | None = None


class TaskUpdate(BaseModel):
    """Schema for updating a task"""
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    completed: bool | None = None
    project_id: UUID | None = None
    section_id: UUID | None = None
    order_index: int | None = None
    priority_id: UUID | None = None
    due_datetime: datetime | None = None
    reminder_minutes: int | None = None  # Minutes before due_datetime to send notification
    duration_minutes: int | None = None  # Estimated time to complete task in minutes
    recurrence_interval: int | None = None
    recurrence_unit: str | None = None
    recurrence_days: list[int] | None = None
    label_ids: list[UUID] | None = None


class TaskResponse(BaseModel):
    """Schema for task responses"""
    id: UUID
    title: str
    description: str | None
    completed: bool
    archived: bool
    order_index: int
    snooze_count: int
    project_id: UUID
    section_id: UUID
    priority_id: UUID | None
    due_datetime: datetime | None
    reminder_minutes: int | None
    duration_minutes: int | None
    recurrence_interval: int | None
    recurrence_unit: str | None
    recurrence_days: list[int] | None
    created_at: datetime
    updated_at: datetime
    labels: list[LabelResponse]

    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)


class TaskReorder(BaseModel):
    """Schema for reordering tasks"""
    id: UUID
    project_id: UUID
    section_id: UUID
    order_index: int


class TaskCountsByProjectResponse(BaseModel):
    """Response schema for active task counts grouped by project."""

    # Map of project_id (UUID as string) to count of active tasks
    counts: dict[str, int]
