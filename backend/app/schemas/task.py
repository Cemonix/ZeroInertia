from datetime import datetime
from typing import ClassVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.label import LabelResponse


class TaskCreate(BaseModel):
    """Schema for creating a task"""
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    project_id: UUID
    section_id: UUID
    priority_id: UUID | None = None
    due_datetime: datetime | None = None
    label_ids: list[UUID] | None = None


class TaskUpdate(BaseModel):
    """Schema for updating a task"""
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    completed: bool | None = None
    order_index: int | None = None
    priority_id: UUID | None = None
    due_datetime: datetime | None = None
    label_ids: list[UUID] | None = None


class TaskResponse(BaseModel):
    """Schema for task responses"""
    id: UUID
    title: str
    description: str | None
    completed: bool
    order_index: int
    project_id: UUID
    section_id: UUID
    priority_id: UUID | None
    due_datetime: datetime | None
    created_at: datetime
    updated_at: datetime
    labels: list[LabelResponse]

    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)


class TaskReorder(BaseModel):
    """Schema for reordering tasks"""
    id: UUID
    section_id: UUID
    order_index: int
