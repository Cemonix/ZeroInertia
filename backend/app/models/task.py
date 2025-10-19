from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Text

from app.models.base import Base


class Task(Base):
    __tablename__: str = "tasks"

    # Primary key with UUID
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    # Task fields - required
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    completed: Mapped[bool] = mapped_column(default=False, nullable=False)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    section_id: Mapped[UUID] = mapped_column(ForeignKey("sections.id", ondelete="CASCADE"), nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="tasks")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821
    project: Mapped["Project"] = relationship(back_populates="tasks")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821
    section: Mapped["Section"] = relationship(back_populates="tasks")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821

    # Constraints and Indexes
    __table_args__: tuple[Index] = (
        Index("ix_tasks_user_id", "user_id"),
    )
