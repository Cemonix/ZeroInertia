from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Text

from app.models.base import Base


class Media(Base):
    """Base model for all media types using joined table inheritance."""

    __tablename__: str = "media"

    # Primary key with UUID
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    # Common fields for all media types
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    media_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'book', 'movie', 'game', 'show'
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)  # 'planned', 'in_progress', 'completed', 'dropped'
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 0-100 percentage
    started_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    completed_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Polymorphic configuration for joined table inheritance
    __mapper_args__: dict[str, str | object] = {
        "polymorphic_identity": "media",
        "polymorphic_on": "media_type",
        "with_polymorphic": "*",
    }

    # Relationships
    user: Mapped["User"] = relationship(back_populates="media_items")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821

    # Indexes
    __table_args__: tuple[Index, ...] = (
        Index("ix_media_user_id", "user_id"),
        Index("ix_media_status", "status"),
        Index("ix_media_media_type", "media_type"),
    )


class Book(Media):
    """Book-specific media model."""

    __tablename__: str = "books"

    # Foreign key to parent media table
    id: Mapped[UUID] = mapped_column(ForeignKey("media.id", ondelete="CASCADE"), primary_key=True)

    # Book-specific fields
    author: Mapped[str] = mapped_column(String(255), nullable=False)
    pages: Mapped[int | None] = mapped_column(Integer, nullable=True)
    isbn: Mapped[str | None] = mapped_column(String(20), nullable=True)
    publisher: Mapped[str | None] = mapped_column(String(255), nullable=True)

    __mapper_args__: dict[str, str | object] = {
        "polymorphic_identity": "book",
    }


class Movie(Media):
    """Movie-specific media model."""

    __tablename__: str = "movies"

    # Foreign key to parent media table
    id: Mapped[UUID] = mapped_column(ForeignKey("media.id", ondelete="CASCADE"), primary_key=True)

    # Movie-specific fields
    director: Mapped[str | None] = mapped_column(String(255), nullable=True)
    duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    release_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    genre: Mapped[str | None] = mapped_column(String(100), nullable=True)

    __mapper_args__: dict[str, str | object] = {
        "polymorphic_identity": "movie",
    }


class Game(Media):
    """Game-specific media model."""

    __tablename__: str = "games"

    # Foreign key to parent media table
    id: Mapped[UUID] = mapped_column(ForeignKey("media.id", ondelete="CASCADE"), primary_key=True)

    # Game-specific fields
    platform: Mapped[str | None] = mapped_column(String(100), nullable=True)  # 'PS5', 'PC', 'Switch', etc.
    developer: Mapped[str | None] = mapped_column(String(255), nullable=True)
    playtime_hours: Mapped[int | None] = mapped_column(Integer, nullable=True)
    genre: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_100_percent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # Platinum/100% completion

    __mapper_args__: dict[str, str | object] = {
        "polymorphic_identity": "game",
    }


class Show(Media):
    """TV Show-specific media model (per season tracking)."""

    __tablename__: str = "shows"

    # Foreign key to parent media table
    id: Mapped[UUID] = mapped_column(ForeignKey("media.id", ondelete="CASCADE"), primary_key=True)

    # Show-specific fields
    season_number: Mapped[int | None] = mapped_column(Integer, nullable=True)  # Track individual seasons
    episodes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    creator: Mapped[str | None] = mapped_column(String(255), nullable=True)
    release_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    genre: Mapped[str | None] = mapped_column(String(100), nullable=True)

    __mapper_args__: dict[str, str | object] = {
        "polymorphic_identity": "show",
    }
