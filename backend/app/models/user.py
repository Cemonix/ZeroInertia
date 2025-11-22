from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Index, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class User(Base):
    __tablename__: str = "users"

    # Primary key with UUID
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    # OAuth fields - required
    oauth_provider: Mapped[str] = mapped_column(String(50))
    oauth_subject_id: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255))

    # Optional user info
    full_name: Mapped[str | None] = mapped_column(String(255))
    avatar_url: Mapped[str | None] = mapped_column(String(500))

    # Timestamps
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=None)

    # Relationships
    projects: Mapped[list["Project"]] = relationship(back_populates="user", cascade="all, delete-orphan")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821
    sections: Mapped[list["Section"]] = relationship(back_populates="user", cascade="all, delete-orphan")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821
    tasks: Mapped[list["Task"]] = relationship(back_populates="user", cascade="all, delete-orphan")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821
    streaks: Mapped[list["Streak"]] = relationship(back_populates="user", cascade="all, delete-orphan")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821
    labels: Mapped[list["Label"]] = relationship(back_populates="user", cascade="all, delete-orphan")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821
    notes: Mapped[list["Note"]] = relationship(back_populates="user", cascade="all, delete-orphan")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821
    push_subscriptions: Mapped[list["PushSubscription"]] = relationship(back_populates="user", cascade="all, delete-orphan")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821
    books: Mapped[list["Book"]] = relationship(back_populates="user", cascade="all, delete-orphan")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821
    games: Mapped[list["Game"]] = relationship(back_populates="user", cascade="all, delete-orphan")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821
    movies: Mapped[list["Movie"]] = relationship(back_populates="user", cascade="all, delete-orphan")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821
    shows: Mapped[list["Show"]] = relationship(back_populates="user", cascade="all, delete-orphan")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821
    manga: Mapped[list["Manga"]] = relationship(back_populates="user", cascade="all, delete-orphan")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821
    anime: Mapped[list["Anime"]] = relationship(back_populates="user", cascade="all, delete-orphan")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821
    genres: Mapped[list["Genre"]] = relationship(back_populates="user", cascade="all, delete-orphan")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821

    # Constraints and Indexes
    __table_args__: tuple[UniqueConstraint, UniqueConstraint, Index] = (
        UniqueConstraint("oauth_provider", "oauth_subject_id", name="uq_oauth_provider_subject"),
        UniqueConstraint("email", name="uq_email"),
        Index("ix_oauth_provider", "oauth_provider", "email"),
    )
