from datetime import date, datetime
from enum import Enum
from typing import ClassVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MediaStatus(str, Enum):
    """Enum for media status"""

    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DROPPED = "dropped"


# ===== Book Schemas =====


class BookCreate(BaseModel):
    """Schema for creating a book"""

    title: str = Field(..., min_length=1, max_length=500)
    creator: str = Field(..., min_length=1, max_length=255)
    status: MediaStatus = MediaStatus.PLANNED
    genre: str | None = Field(None, max_length=100)
    started_at: date | None = None
    completed_at: date | None = None
    notes: str | None = None


class BookUpdate(BaseModel):
    """Schema for updating a book"""

    title: str | None = Field(None, min_length=1, max_length=500)
    creator: str | None = Field(None, min_length=1, max_length=255)
    status: MediaStatus | None = None
    genre: str | None = Field(None, max_length=100)
    started_at: date | None = None
    completed_at: date | None = None
    notes: str | None = None


class BookResponse(BaseModel):
    """Schema for book responses"""

    id: UUID
    title: str
    creator: str
    status: str
    genre: str | None
    started_at: date | None
    completed_at: date | None
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)


# ===== Movie Schemas =====


class MovieCreate(BaseModel):
    """Schema for creating a movie"""

    title: str = Field(..., min_length=1, max_length=500)
    status: MediaStatus = MediaStatus.PLANNED
    genre: str | None = Field(None, max_length=100)
    started_at: date | None = None
    completed_at: date | None = None
    notes: str | None = None


class MovieUpdate(BaseModel):
    """Schema for updating a movie"""

    title: str | None = Field(None, min_length=1, max_length=500)
    status: MediaStatus | None = None
    genre: str | None = Field(None, max_length=100)
    started_at: date | None = None
    completed_at: date | None = None
    notes: str | None = None


class MovieResponse(BaseModel):
    """Schema for movie responses"""

    id: UUID
    title: str
    status: str
    genre: str | None
    started_at: date | None
    completed_at: date | None
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)


# ===== Game Schemas =====


class GameCreate(BaseModel):
    """Schema for creating a game"""

    title: str = Field(..., min_length=1, max_length=500)
    status: MediaStatus = MediaStatus.PLANNED
    genre: str | None = Field(None, max_length=100)
    platform: str | None = Field(None, max_length=100)
    started_at: date | None = None
    completed_at: date | None = None
    notes: str | None = None


class GameUpdate(BaseModel):
    """Schema for updating a game"""

    title: str | None = Field(None, min_length=1, max_length=500)
    status: MediaStatus | None = None
    genre: str | None = Field(None, max_length=100)
    platform: str | None = Field(None, max_length=100)
    started_at: date | None = None
    completed_at: date | None = None
    notes: str | None = None


class GameResponse(BaseModel):
    """Schema for game responses"""

    id: UUID
    title: str
    status: str
    genre: str | None
    platform: str | None
    started_at: date | None
    completed_at: date | None
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)


# ===== Show Schemas =====


class ShowCreate(BaseModel):
    """Schema for creating a TV show season"""

    title: str = Field(..., min_length=1, max_length=500)
    season_number: int | None = Field(None, gt=0)
    status: MediaStatus = MediaStatus.PLANNED
    genre: str | None = Field(None, max_length=100)
    started_at: date | None = None
    completed_at: date | None = None
    notes: str | None = None


class ShowUpdate(BaseModel):
    """Schema for updating a TV show season"""

    title: str | None = Field(None, min_length=1, max_length=500)
    season_number: int | None = Field(None, gt=0)
    status: MediaStatus | None = None
    genre: str | None = Field(None, max_length=100)
    started_at: date | None = None
    completed_at: date | None = None
    notes: str | None = None


class ShowResponse(BaseModel):
    """Schema for TV show responses"""

    id: UUID
    title: str
    season_number: int | None
    status: str
    genre: str | None
    started_at: date | None
    completed_at: date | None
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)


# ===== Utility Schemas =====


class DuplicateCheckResponse(BaseModel):
    """Schema for duplicate check responses"""

    books: list[dict[str, str | None]] = []
    games: list[dict[str, str | None]] = []
    movies: list[dict[str, str | None]] = []
    shows: list[dict[str, str | None]] = []

class YearlyStatsResponse(BaseModel):
    """Schema for yearly statistics responses"""

    year: int
    books: int
    games: int
    movies: int
    shows: int
