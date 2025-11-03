from datetime import date, datetime, time
from enum import StrEnum
from typing import ClassVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator


class RecurrenceTypeEnum(StrEnum):
    DAILY = "daily"
    WEEKLY = "weekly"
    ALTERNATE_DAYS = "alternate_days"


class RecurringTaskCreate(BaseModel):
    """Schema for creating a recurring task"""
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    project_id: UUID
    section_id: UUID
    priority_id: UUID | None = None
    label_ids: list[UUID] | None = None

    # Recurrence configuration
    recurrence_type: RecurrenceTypeEnum
    recurrence_days: list[int] | None = Field(
        None,
        description="Array of weekday integers (0=Monday, 6=Sunday) for weekly recurrence"
    )
    recurrence_time: time = Field(..., description="Time of day when task should be created")
    start_date: date = Field(..., description="Date when recurrence starts")
    end_date: date | None = Field(None, description="Optional date when recurrence ends")
    is_active: bool = True

    @field_validator("recurrence_days")
    @classmethod
    def validate_recurrence_days(cls, v: list[int] | None, info: ValidationInfo) -> list[int] | None:
        """Validate recurrence_days based on recurrence_type"""
        recurrence_type = info.data.get("recurrence_type")

        if recurrence_type == "weekly":
            if v is None or len(v) == 0:
                raise ValueError("recurrence_days must contain at least one day for weekly recurrence")
        else:
            if v is not None:
                raise ValueError("recurrence_days is only allowed for weekly recurrence")
            return None

        # Check all values are valid weekday numbers (0-6)
        if not all(0 <= day <= 6 for day in v):
            raise ValueError("recurrence_days must contain integers between 0 (Monday) and 6 (Sunday)")
        # Check for duplicates
        if len(v) != len(set(v)):
            raise ValueError("recurrence_days must not contain duplicate values")
        # Sort for consistency
        v = sorted(v)

        return v

    @field_validator("end_date")
    @classmethod
    def validate_end_date(cls, v: date | None, info: ValidationInfo) -> date | None:
        """Validate that end_date is after start_date"""
        if v is not None and "start_date" in info.data:
            start_date = info.data["start_date"]  # pyright: ignore[reportAny]
            if v <= start_date:
                raise ValueError("end_date must be after start_date")
        return v


class RecurringTaskUpdate(BaseModel):
    """Schema for updating a recurring task"""
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    priority_id: UUID | None = None
    label_ids: list[UUID] | None = None

    # Recurrence configuration
    recurrence_type: RecurrenceTypeEnum | None = None
    recurrence_days: list[int] | None = None
    recurrence_time: time | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_active: bool | None = None

    @field_validator("recurrence_days")
    @classmethod
    def validate_recurrence_days(cls, v: list[int] | None) -> list[int] | None:
        """Validate recurrence_days values"""
        if v is not None:
            if not all(0 <= day <= 6 for day in v):
                raise ValueError("recurrence_days must contain integers between 0 (Monday) and 6 (Sunday)")
            if len(v) != len(set(v)):
                raise ValueError("recurrence_days must not contain duplicate values")
            v = sorted(v)
        return v


class RecurringTaskResponse(BaseModel):
    """Schema for recurring task responses"""
    id: UUID
    title: str
    description: str | None
    project_id: UUID
    section_id: UUID
    priority_id: UUID | None
    label_ids: list[UUID] | None

    # Recurrence configuration
    recurrence_type: str
    recurrence_days: list[int] | None
    recurrence_time: time
    start_date: date
    end_date: date | None

    # Tracking
    last_generated_date: date | None
    is_active: bool

    # Timestamps
    created_at: datetime
    updated_at: datetime

    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)
