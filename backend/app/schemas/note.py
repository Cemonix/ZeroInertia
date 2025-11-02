from datetime import datetime
from typing import ClassVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class NoteCreate(BaseModel):
    """Schema for creating a note."""

    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field("", description="Markdown content for the note")
    parent_id: UUID | None = Field(default=None)
    order_index: int | None = Field(default=None, ge=0)


class NoteUpdate(BaseModel):
    """Schema for partially updating a note."""

    title: str | None = Field(None, min_length=1, max_length=255)
    content: str | None = Field(None, description="Updated markdown content")
    parent_id: UUID | None = Field(None)
    order_index: int | None = Field(None, ge=0)


class NoteResponse(BaseModel):
    """Schema returned for note entities."""

    id: UUID
    title: str
    content: str
    parent_id: UUID | None
    order_index: int
    created_at: datetime
    updated_at: datetime

    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)


class NoteReorder(BaseModel):
    """Schema for reordering notes."""

    id: UUID
    parent_id: UUID | None
    order_index: int = Field(ge=0)
