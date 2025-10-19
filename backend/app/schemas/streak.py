from datetime import date
from typing import ClassVar

from pydantic import BaseModel, ConfigDict


class StreakResponse(BaseModel):
    """Response schema for streak statistics."""

    current_streak: int
    longest_streak: int
    last_activity_date: date | None

    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)
