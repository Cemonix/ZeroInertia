from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Text

from app.models.base import Base


class Book(Base):
    """Book model - independent table for book tracking."""

    __tablename__: str = "books"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    creator: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="planned")
    is_audiobook: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    started_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    completed_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user: Mapped["User"] = relationship(back_populates="books")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821
    genres: Mapped[list["Genre"]] = relationship(secondary="book_genres", back_populates="books")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821

    __table_args__: tuple[Index | CheckConstraint, ...] = (
        Index("idx_books_user", "user_id"),
        Index("idx_books_status", "user_id", "status"),
        Index("idx_books_completed", "user_id", "completed_at"),
        Index("idx_books_title", "title"),
        CheckConstraint("status IN ('planned', 'in_progress', 'completed', 'dropped')", name="chk_books_status"),
    )


class Game(Base):
    """Game model - independent table for game tracking."""

    __tablename__: str = "games"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="planned")
    platform: Mapped[str | None] = mapped_column(String(100), nullable=True)
    started_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    completed_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user: Mapped["User"] = relationship(back_populates="games")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821
    genres: Mapped[list["Genre"]] = relationship(secondary="game_genres", back_populates="games")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821

    __table_args__: tuple[Index | CheckConstraint, ...] = (
        Index("idx_games_user", "user_id"),
        Index("idx_games_status", "user_id", "status"),
        Index("idx_games_completed", "user_id", "completed_at"),
        Index("idx_games_title", "title"),
        CheckConstraint("status IN ('planned', 'in_progress', 'completed', 'dropped')", name="chk_games_status"),
    )


class Movie(Base):
    """Movie model - independent table for movie tracking."""

    __tablename__: str = "movies"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="planned")
    started_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    completed_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user: Mapped["User"] = relationship(back_populates="movies")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821
    genres: Mapped[list["Genre"]] = relationship(secondary="movie_genres", back_populates="movies")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821

    __table_args__: tuple[Index | CheckConstraint, ...] = (
        Index("idx_movies_user", "user_id"),
        Index("idx_movies_status", "user_id", "status"),
        Index("idx_movies_completed", "user_id", "completed_at"),
        Index("idx_movies_title", "title"),
        CheckConstraint("status IN ('planned', 'in_progress', 'completed', 'dropped')", name="chk_movies_status"),
    )


class Show(Base):
    """TV Show model - independent table for show season tracking."""

    __tablename__: str = "shows"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    season_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="planned")
    started_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    completed_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user: Mapped["User"] = relationship(back_populates="shows")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821
    genres: Mapped[list["Genre"]] = relationship(secondary="show_genres", back_populates="shows")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821

    __table_args__: tuple[Index | CheckConstraint, ...] = (
        Index("idx_shows_user", "user_id"),
        Index("idx_shows_status", "user_id", "status"),
        Index("idx_shows_completed", "user_id", "completed_at"),
        Index("idx_shows_title", "title"),
        CheckConstraint("status IN ('planned', 'in_progress', 'completed', 'dropped')", name="chk_shows_status"),
    )


class Manga(Base):
    """Manga model - independent table for manga tracking."""

    __tablename__: str = "manga"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    author: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="planned")
    started_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    completed_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user: Mapped["User"] = relationship(back_populates="manga")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821
    genres: Mapped[list["Genre"]] = relationship(secondary="manga_genres", back_populates="manga")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821

    __table_args__: tuple[Index | CheckConstraint, ...] = (
        Index("idx_manga_user", "user_id"),
        Index("idx_manga_status", "user_id", "status"),
        Index("idx_manga_completed", "user_id", "completed_at"),
        Index("idx_manga_title", "title"),
        CheckConstraint("status IN ('planned', 'in_progress', 'completed', 'dropped')", name="chk_manga_status"),
    )
