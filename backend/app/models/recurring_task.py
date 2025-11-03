from datetime import date, datetime, time
from uuid import UUID, uuid4

from sqlalchemy import Date, DateTime, ForeignKey, Index, Integer, String, Time, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Text

from app.models.base import Base


class RecurringTask(Base):
    __tablename__: str = "recurring_tasks"

    # Primary key with UUID
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    # Template fields for generated tasks
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Recurrence configuration - values: daily | weekly | alternate_days
    recurrence_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # Array of integers for weekly recurrences.
    # IMPORTANT: Uses Python's weekday() convention (0=Monday, 1=Tuesday, ..., 6=Sunday).
    # Frontend must convert from JavaScript's getDay() (0=Sunday) before sending.
    recurrence_days: Mapped[list[int] | None] = mapped_column(ARRAY(Integer), nullable=True)

    # Time of day when task should be due (e.g., "09:00")
    recurrence_time: Mapped[time] = mapped_column(Time, nullable=False)

    # Date range for recurrence
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Tracking
    last_generated_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Foreign keys
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    section_id: Mapped[UUID] = mapped_column(ForeignKey("sections.id", ondelete="CASCADE"), nullable=False)
    priority_id: Mapped[UUID | None] = mapped_column(ForeignKey("priorities.id", ondelete="SET NULL"), nullable=True)

    # Store label IDs as array to apply to generated tasks
    label_ids: Mapped[list[UUID] | None] = mapped_column(ARRAY(PG_UUID(as_uuid=True)), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="recurring_tasks")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821
    project: Mapped["Project"] = relationship(back_populates="recurring_tasks")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821
    section: Mapped["Section"] = relationship(back_populates="recurring_tasks")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821
    priority: Mapped["Priority | None"] = relationship(back_populates="recurring_tasks")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821
    generated_tasks: Mapped[list["Task"]] = relationship(back_populates="recurring_task")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821

    # Constraints and Indexes
    __table_args__: tuple[Index, Index] = (
        Index("ix_recurring_tasks_user_id", "user_id"),
        Index("ix_recurring_tasks_is_active", "is_active"),
    )
