from datetime import datetime
from typing import ClassVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TaskCreate(BaseModel):
    """Schema for creating a task"""
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    project_id: UUID
    section_id: UUID


class TaskUpdate(BaseModel):
    """Schema for updating a task"""
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    completed: bool | None = None


class TaskResponse(BaseModel):
    """Schema for task responses"""
    id: UUID
    title: str
    description: str | None
    completed: bool
    project_id: UUID
    section_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)
