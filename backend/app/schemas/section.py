from datetime import datetime
from typing import ClassVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SectionCreate(BaseModel):
    """Schema for creating a section"""
    title: str = Field(..., min_length=1, max_length=255)
    project_id: UUID | None = Field(None)
    order_index: int = Field(0)

class SectionUpdate(BaseModel):
    """Schema for updating a section"""
    title: str | None = Field(None, min_length=1, max_length=255)
    project_id: UUID | None = Field(None)
    order_index: int | None = Field(None)


class SectionResponse(BaseModel):
    """Schema for section responses"""
    id: UUID
    title: str
    project_id: UUID | None
    order_index: int
    created_at: datetime
    updated_at: datetime

    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)


class SectionReorder(BaseModel):
    """Schema for reordering sections"""
    id: UUID
    project_id: UUID | None
    order_index: int
