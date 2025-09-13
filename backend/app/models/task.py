from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import Enum, ForeignKey, Index, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class TaskStatus(StrEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PriorityLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Task(Base):
    __tablename__: str = "tasks"

    # Primary key with UUID
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    template_id: Mapped[UUID | None] = mapped_column(ForeignKey("templates.id", ondelete="SET NULL"), default=None)

    parent_id: Mapped[UUID | None] = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"), default=None)
    order_index: Mapped[int] = mapped_column(default=0)

    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(String(1000), default=None)
    priority: Mapped[PriorityLevel] = mapped_column(Enum(PriorityLevel), default=PriorityLevel.LOW)
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), default=TaskStatus.PENDING)

    time_spent: Mapped[int] = mapped_column(default=0)  # in seconds

    scheduled_date: Mapped[datetime | None] = mapped_column(default=None)
    due_date: Mapped[datetime | None] = mapped_column(default=None)
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(default=None)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="tasks")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821
    subtasks: Mapped[list["Task"]] = relationship(
        back_populates="parent", cascade="all, delete-orphan"
    )
    parent: Mapped["Task"] | None = relationship(back_populates="subtasks", remote_side=[id])
    template: Mapped["TaskTemplate"] | None = relationship(back_populates="tasks")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821
    labels: Mapped[list["Label"]] = relationship(  # pyright: ignore[reportUndefinedVariable]  # noqa: F821
        secondary="task_labels",
        back_populates="tasks",
    )

    __table_args__: tuple[Index | UniqueConstraint, ...] = (
        Index("ix_user_id", "user_id"),
        Index("ix_user_id_status", "user_id", "status"),
        Index("ix_user_id_scheduled_date", "user_id", "scheduled_date"),
        Index("ix_template_id", "template_id"),
        Index("ix_parent_id", "parent_id"),
        UniqueConstraint("user_id", "parent_id", "order_index", name="uq_user_parent_order"),
        Index("ix_user_id_parent_id_order_index", "user_id", "parent_id", "order_index"),
    )
