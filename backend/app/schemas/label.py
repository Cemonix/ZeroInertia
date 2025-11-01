from datetime import datetime
from typing import ClassVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class LabelCreate(BaseModel):
    """Schema for creating a label."""
    name: str = Field(..., min_length=1, max_length=100)
    color: str | None = Field(default=None, min_length=4, max_length=7)
    description: str | None = Field(default=None, max_length=255)
    order_index: int | None = Field(default=None, ge=0)


class LabelUpdate(BaseModel):
    """Schema for updating a label."""
    name: str | None = Field(default=None, min_length=1, max_length=100)
    color: str | None = Field(default=None, min_length=4, max_length=7)
    description: str | None = Field(default=None, max_length=255)
    order_index: int | None = Field(default=None, ge=0)


class LabelResponse(BaseModel):
    """Schema for label responses."""
    id: UUID
    name: str
    color: str | None
    description: str | None
    order_index: int
    created_at: datetime
    updated_at: datetime

    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)
