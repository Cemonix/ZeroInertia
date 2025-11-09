from datetime import date, datetime
from enum import Enum
from typing import ClassVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MediaType(str, Enum):
    """Enum for media types"""

    BOOK = "book"
    MOVIE = "movie"
    GAME = "game"
    SHOW = "show"


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
    author: str = Field(..., min_length=1, max_length=255)
    pages: int | None = Field(None, gt=0)
    isbn: str | None = Field(None, max_length=20)
    publisher: str | None = Field(None, max_length=255)
    status: MediaStatus = MediaStatus.PLANNED
    rating: int | None = Field(None, ge=0, le=100)  # 0-100 percentage
    started_at: date | None = None
    completed_at: date | None = None
    notes: str | None = None


class BookUpdate(BaseModel):
    """Schema for updating a book"""

    title: str | None = Field(None, min_length=1, max_length=500)
    author: str | None = Field(None, min_length=1, max_length=255)
    pages: int | None = Field(None, gt=0)
    isbn: str | None = Field(None, max_length=20)
    publisher: str | None = Field(None, max_length=255)
    status: MediaStatus | None = None
    rating: int | None = Field(None, ge=0, le=100)
    started_at: date | None = None
    completed_at: date | None = None
    notes: str | None = None


class BookResponse(BaseModel):
    """Schema for book responses"""

    id: UUID
    media_type: MediaType
    title: str
    author: str
    pages: int | None
    isbn: str | None
    publisher: str | None
    status: str
    rating: int | None
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
    director: str | None = Field(None, max_length=255)
    duration_minutes: int | None = Field(None, gt=0)
    release_year: int | None = Field(None, ge=1800, le=2100)
    genre: str | None = Field(None, max_length=100)
    status: MediaStatus = MediaStatus.PLANNED
    rating: int | None = Field(None, ge=0, le=100)
    started_at: date | None = None
    completed_at: date | None = None
    notes: str | None = None


class MovieUpdate(BaseModel):
    """Schema for updating a movie"""

    title: str | None = Field(None, min_length=1, max_length=500)
    director: str | None = Field(None, max_length=255)
    duration_minutes: int | None = Field(None, gt=0)
    release_year: int | None = Field(None, ge=1800, le=2100)
    genre: str | None = Field(None, max_length=100)
    status: MediaStatus | None = None
    rating: int | None = Field(None, ge=0, le=100)
    started_at: date | None = None
    completed_at: date | None = None
    notes: str | None = None


class MovieResponse(BaseModel):
    """Schema for movie responses"""

    id: UUID
    media_type: MediaType
    title: str
    director: str | None
    duration_minutes: int | None
    release_year: int | None
    genre: str | None
    status: str
    rating: int | None
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
    platform: str | None = Field(None, max_length=100)
    developer: str | None = Field(None, max_length=255)
    playtime_hours: int | None = Field(None, gt=0)
    genre: str | None = Field(None, max_length=100)
    is_100_percent: bool = False
    status: MediaStatus = MediaStatus.PLANNED
    rating: int | None = Field(None, ge=0, le=100)
    started_at: date | None = None
    completed_at: date | None = None
    notes: str | None = None


class GameUpdate(BaseModel):
    """Schema for updating a game"""

    title: str | None = Field(None, min_length=1, max_length=500)
    platform: str | None = Field(None, max_length=100)
    developer: str | None = Field(None, max_length=255)
    playtime_hours: int | None = Field(None, gt=0)
    genre: str | None = Field(None, max_length=100)
    is_100_percent: bool | None = None
    status: MediaStatus | None = None
    rating: int | None = Field(None, ge=0, le=100)
    started_at: date | None = None
    completed_at: date | None = None
    notes: str | None = None


class GameResponse(BaseModel):
    """Schema for game responses"""

    id: UUID
    media_type: MediaType
    title: str
    platform: str | None
    developer: str | None
    playtime_hours: int | None
    genre: str | None
    is_100_percent: bool
    status: str
    rating: int | None
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
    episodes: int | None = Field(None, gt=0)
    creator: str | None = Field(None, max_length=255)
    release_year: int | None = Field(None, ge=1800, le=2100)
    genre: str | None = Field(None, max_length=100)
    status: MediaStatus = MediaStatus.PLANNED
    rating: int | None = Field(None, ge=0, le=100)
    started_at: date | None = None
    completed_at: date | None = None
    notes: str | None = None


class ShowUpdate(BaseModel):
    """Schema for updating a TV show season"""

    title: str | None = Field(None, min_length=1, max_length=500)
    season_number: int | None = Field(None, gt=0)
    episodes: int | None = Field(None, gt=0)
    creator: str | None = Field(None, max_length=255)
    release_year: int | None = Field(None, ge=1800, le=2100)
    genre: str | None = Field(None, max_length=100)
    status: MediaStatus | None = None
    rating: int | None = Field(None, ge=0, le=100)
    started_at: date | None = None
    completed_at: date | None = None
    notes: str | None = None


class ShowResponse(BaseModel):
    """Schema for TV show responses"""

    id: UUID
    media_type: MediaType
    title: str
    season_number: int | None
    episodes: int | None
    creator: str | None
    release_year: int | None
    genre: str | None
    status: str
    rating: int | None
    started_at: date | None
    completed_at: date | None
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)
