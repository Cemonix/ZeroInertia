from typing import ClassVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class UserResponse(BaseModel):
    """Schema for user responses"""
    id: UUID
    email: str
    full_name: str | None = None
    avatar_url: str | None = None

    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)
