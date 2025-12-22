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


# ===== Genre Schemas =====


class GenreCreate(BaseModel):
    """Schema for creating a genre"""

    name: str = Field(..., min_length=1, max_length=100)


class GenreUpdate(BaseModel):
    """Schema for updating a genre"""

    name: str = Field(..., min_length=1, max_length=100)


class GenreResponse(BaseModel):
    """Schema for genre responses"""

    id: UUID
    name: str
    created_at: datetime

    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)


# ===== Book Schemas =====


class BookCreate(BaseModel):
    """Schema for creating a book"""

    title: str = Field(..., min_length=1, max_length=500)
    creator: str = Field(..., min_length=1, max_length=255)
    status: MediaStatus = MediaStatus.PLANNED
    is_audiobook: bool = False
    genre_ids: list[UUID] = Field(default_factory=list)
    started_at: date | None = None
    completed_at: date | None = None
    notes: str | None = None


class BookUpdate(BaseModel):
    """Schema for updating a book"""

    title: str | None = Field(None, min_length=1, max_length=500)
    creator: str | None = Field(None, min_length=1, max_length=255)
    status: MediaStatus | None = None
    is_audiobook: bool | None = None
    genre_ids: list[UUID] | None = None
    started_at: date | None = None
    completed_at: date | None = None
    notes: str | None = None


class BookResponse(BaseModel):
    """Schema for book responses"""

    id: UUID
    title: str
    creator: str
    status: str
    is_audiobook: bool
    genres: list[GenreResponse]
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
    genre_ids: list[UUID] = Field(default_factory=list)
    completed_at: date | None = None
    notes: str | None = None


class MovieUpdate(BaseModel):
    """Schema for updating a movie"""

    title: str | None = Field(None, min_length=1, max_length=500)
    status: MediaStatus | None = None
    genre_ids: list[UUID] | None = None
    completed_at: date | None = None
    notes: str | None = None


class MovieResponse(BaseModel):
    """Schema for movie responses"""

    id: UUID
    title: str
    status: str
    genres: list[GenreResponse]
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
    genre_ids: list[UUID] = Field(default_factory=list)
    platform: str | None = Field(None, max_length=100)
    started_at: date | None = None
    completed_at: date | None = None
    notes: str | None = None


class GameUpdate(BaseModel):
    """Schema for updating a game"""

    title: str | None = Field(None, min_length=1, max_length=500)
    status: MediaStatus | None = None
    genre_ids: list[UUID] | None = None
    platform: str | None = Field(None, max_length=100)
    started_at: date | None = None
    completed_at: date | None = None
    notes: str | None = None


class GameResponse(BaseModel):
    """Schema for game responses"""

    id: UUID
    title: str
    status: str
    genres: list[GenreResponse]
    platform: str | None
    started_at: date | None
    completed_at: date | None
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)


# ===== Show Schemas =====


class ShowCreate(BaseModel):
    """Schema for creating a TV show"""

    title: str = Field(..., min_length=1, max_length=500)
    status: MediaStatus = MediaStatus.PLANNED
    genre_ids: list[UUID] = Field(default_factory=list)
    started_at: date | None = None
    completed_at: date | None = None
    notes: str | None = None


class ShowUpdate(BaseModel):
    """Schema for updating a TV show"""

    title: str | None = Field(None, min_length=1, max_length=500)
    status: MediaStatus | None = None
    genre_ids: list[UUID] | None = None
    started_at: date | None = None
    completed_at: date | None = None
    notes: str | None = None


class ShowResponse(BaseModel):
    """Schema for TV show responses"""

    id: UUID
    title: str
    status: str
    genres: list[GenreResponse]
    started_at: date | None
    completed_at: date | None
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)


# ===== Manga Schemas =====


class MangaCreate(BaseModel):
    """Schema for creating a manga"""

    title: str = Field(..., min_length=1, max_length=500)
    author: str | None = Field(None, max_length=255)
    status: MediaStatus = MediaStatus.PLANNED
    genre_ids: list[UUID] = Field(default_factory=list)
    started_at: date | None = None
    completed_at: date | None = None
    notes: str | None = None


class MangaUpdate(BaseModel):
    """Schema for updating a manga"""

    title: str | None = Field(None, min_length=1, max_length=500)
    author: str | None = Field(None, max_length=255)
    status: MediaStatus | None = None
    genre_ids: list[UUID] | None = None
    started_at: date | None = None
    completed_at: date | None = None
    notes: str | None = None


class MangaResponse(BaseModel):
    """Schema for manga responses"""

    id: UUID
    title: str
    author: str | None
    status: str
    genres: list[GenreResponse]
    started_at: date | None
    completed_at: date | None
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)


# ===== Anime Schemas =====


class AnimeCreate(BaseModel):
    """Schema for creating an anime"""

    title: str = Field(..., min_length=1, max_length=500)
    episodes: int | None = None
    status: MediaStatus = MediaStatus.PLANNED
    genre_ids: list[UUID] = Field(default_factory=list)
    started_at: date | None = None
    completed_at: date | None = None
    notes: str | None = None


class AnimeUpdate(BaseModel):
    """Schema for updating an anime"""

    title: str | None = Field(None, min_length=1, max_length=500)
    episodes: int | None = None
    status: MediaStatus | None = None
    genre_ids: list[UUID] | None = None
    started_at: date | None = None
    completed_at: date | None = None
    notes: str | None = None


class AnimeResponse(BaseModel):
    """Schema for anime responses"""

    id: UUID
    title: str
    episodes: int | None
    status: str
    genres: list[GenreResponse]
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
    manga: list[dict[str, str | None]] = []
    anime: list[dict[str, str | None]] = []

class YearlyStatsResponse(BaseModel):
    """Schema for yearly statistics responses"""

    year: int
    books: int
    games: int
    movies: int
    shows: int
    manga: int
    anime: int


# ===== CSV Import Schemas =====


class CSVImportResult(BaseModel):
    """Schema for CSV import results"""

    total_rows: int
    imported: int
    skipped_duplicates: int
    imported_items: list[UUID] = Field(default_factory=list)
    duplicate_titles: list[str] = Field(default_factory=list)
