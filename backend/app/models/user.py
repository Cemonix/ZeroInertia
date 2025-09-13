from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Index, String, UniqueConstraint, func
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
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
    last_login_at: Mapped[datetime | None] = mapped_column(server_default=None)

    # Relationships
    tasks: Mapped[list["Task"]] = relationship(back_populates="user", cascade="all, delete-orphan")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821
    labels: Mapped[list["Label"]] = relationship(back_populates="user", cascade="all, delete-orphan")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821
    task_templates: Mapped[list["TaskTemplate"]] = relationship(back_populates="user", cascade="all, delete-orphan")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821
    task_streaks: Mapped[list["TaskStreak"]] = relationship(back_populates="user", cascade="all, delete-orphan")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821

    # Constraints and Indexes
    __table_args__: tuple[UniqueConstraint, UniqueConstraint, Index] = (
        UniqueConstraint("oauth_provider", "oauth_subject_id", name="uq_oauth_provider_subject"),
        UniqueConstraint("email", name="uq_email"),
        Index("ix_oauth_provider", "oauth_provider", "email"),
    )
