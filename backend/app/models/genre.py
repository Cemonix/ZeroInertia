from datetime import datetime
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy import DateTime, ForeignKey, Index, String, Table, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

book_genres = Table(
    "book_genres",
    Base.metadata,
    sa.Column(
        "book_id",
        sa.Uuid(as_uuid=True),
        ForeignKey("books.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    sa.Column(
        "genre_id",
        sa.Uuid(as_uuid=True),
        ForeignKey("genres.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Index("ix_book_genres_book_id", "book_id"),
    Index("ix_book_genres_genre_id", "genre_id"),
)

game_genres = Table(
    "game_genres",
    Base.metadata,
    sa.Column(
        "game_id",
        sa.Uuid(as_uuid=True),
        ForeignKey("games.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    sa.Column(
        "genre_id",
        sa.Uuid(as_uuid=True),
        ForeignKey("genres.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Index("ix_game_genres_game_id", "game_id"),
    Index("ix_game_genres_genre_id", "genre_id"),
)

movie_genres = Table(
    "movie_genres",
    Base.metadata,
    sa.Column(
        "movie_id",
        sa.Uuid(as_uuid=True),
        ForeignKey("movies.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    sa.Column(
        "genre_id",
        sa.Uuid(as_uuid=True),
        ForeignKey("genres.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Index("ix_movie_genres_movie_id", "movie_id"),
    Index("ix_movie_genres_genre_id", "genre_id"),
)

show_genres = Table(
    "show_genres",
    Base.metadata,
    sa.Column(
        "show_id",
        sa.Uuid(as_uuid=True),
        ForeignKey("shows.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    sa.Column(
        "genre_id",
        sa.Uuid(as_uuid=True),
        ForeignKey("genres.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Index("ix_show_genres_show_id", "show_id"),
    Index("ix_show_genres_genre_id", "genre_id"),
)

manga_genres = Table(
    "manga_genres",
    Base.metadata,
    sa.Column(
        "manga_id",
        sa.Uuid(as_uuid=True),
        ForeignKey("manga.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    sa.Column(
        "genre_id",
        sa.Uuid(as_uuid=True),
        ForeignKey("genres.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Index("ix_manga_genres_manga_id", "manga_id"),
    Index("ix_manga_genres_genre_id", "genre_id"),
)


class Genre(Base):
    """Genre model - user-specific genres shared across media types."""

    __tablename__: str = "genres"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user: Mapped["User"] = relationship(back_populates="genres")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821
    books: Mapped[list["Book"]] = relationship(secondary=book_genres, back_populates="genres")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821
    games: Mapped[list["Game"]] = relationship(secondary=game_genres, back_populates="genres")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821
    movies: Mapped[list["Movie"]] = relationship(secondary=movie_genres, back_populates="genres")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821
    shows: Mapped[list["Show"]] = relationship(secondary=show_genres, back_populates="genres")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821
    manga: Mapped[list["Manga"]] = relationship(secondary=manga_genres, back_populates="genres")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821

    __table_args__: tuple[Index, UniqueConstraint] = (
        Index("ix_genres_user_id", "user_id"),
        UniqueConstraint("user_id", "name", name="uq_genres_user_id_name"),
    )
