from typing import ClassVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PriorityResponse(BaseModel):
    """Schema for priority responses"""
    id: UUID
    name: str
    color: str
    description: str | None
    order_index: int

    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)
