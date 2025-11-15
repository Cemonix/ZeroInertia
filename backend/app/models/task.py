from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Text

from app.models.base import Base
from app.models.label import task_labels


class Task(Base):
    __tablename__: str = "tasks"

    # Primary key with UUID
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    # Task fields - required
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    completed: Mapped[bool] = mapped_column(default=False, nullable=False)
    due_datetime: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    archived: Mapped[bool] = mapped_column(default=False, nullable=False)
    order_index: Mapped[int] = mapped_column(default=0, nullable=False)
    snooze_count: Mapped[int] = mapped_column(default=0, nullable=False)  # Track how many times task was snoozed

    # Reminder field - minutes before due_datetime to send notification
    # Examples: 0 (at due time), 15, 30, 60 (1 hour), 1440 (1 day)
    reminder_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Duration field - estimated time to complete task in minutes
    # Examples: 15, 30, 60 (1 hour), 120 (2 hours)
    # Used for calendar view and time-blocking
    duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Recurrence fields
    recurrence_type: Mapped[str | None] = mapped_column(String(50), nullable=True)  # DEPRECATED: daily | weekly | alternate_days
    recurrence_interval: Mapped[int | None] = mapped_column(Integer, nullable=True)  # How many units between occurrences
    recurrence_unit: Mapped[str | None] = mapped_column(String(20), nullable=True)  # days | weeks | months | years
    recurrence_days: Mapped[list[int] | None] = mapped_column(ARRAY(Integer), nullable=True)  # For weekly: 0=Mon, 6=Sun

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    section_id: Mapped[UUID] = mapped_column(ForeignKey("sections.id", ondelete="CASCADE"), nullable=False)
    priority_id: Mapped[UUID | None] = mapped_column(ForeignKey("priorities.id", ondelete="SET NULL"), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="tasks")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821
    project: Mapped["Project"] = relationship(back_populates="tasks")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821
    section: Mapped["Section"] = relationship(back_populates="tasks")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821
    priority: Mapped["Priority | None"] = relationship(back_populates="tasks")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821
    checklists: Mapped[list["CheckList"]] = relationship(  # pyright: ignore[reportUndefinedVariable]  # noqa: F821
        back_populates="task", cascade="all, delete-orphan", order_by="CheckList.order_index"
    )
    labels: Mapped[list["Label"]] = relationship(  # pyright: ignore[reportUndefinedVariable]  # noqa: F821
        secondary=task_labels,
        back_populates="tasks",
        lazy="selectin",
    )

    # Constraints and Indexes
    __table_args__: tuple[Index] = (
        Index("ix_tasks_user_id", "user_id"),
    )
