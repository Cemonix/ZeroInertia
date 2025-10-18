from datetime import datetime
from typing import ClassVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    """Schema for creating a project"""
    title: str = Field(..., min_length=1, max_length=255)
    parent_id: UUID | None = Field(None)
    order_index: int = Field(0)

class ProjectUpdate(BaseModel):
    """Schema for updating a project"""
    title: str | None = Field(None, min_length=1, max_length=255)
    parent_id: UUID | None = Field(None)
    order_index: int | None = Field(None)


class ProjectResponse(BaseModel):
    """Schema for project responses"""
    id: UUID
    title: str
    parent_id: UUID | None
    order_index: int
    created_at: datetime
    updated_at: datetime

    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)


class ProjectsReorder(BaseModel):
    """Schema for reordering projects"""
    id: UUID
    parent_id: UUID | None
    order_index: int
