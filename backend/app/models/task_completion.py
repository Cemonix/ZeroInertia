from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class TaskCompletion(Base):
    __tablename__: str = "task_completions"

    # Primary key with UUID
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    template_id: Mapped[UUID] = mapped_column(ForeignKey("task_templates.id", ondelete="CASCADE"), nullable=False)
    task_id: Mapped[UUID | None] = mapped_column(ForeignKey("tasks.id", ondelete="SET NULL"), default=None)

    completed_at: Mapped[datetime] = mapped_column()
    time_spent: Mapped[int] = mapped_column(default=0)  # in seconds

    # Relationships
    user: Mapped["User"] = relationship()  # pyright: ignore[reportUndefinedVariable]  # noqa: F821
    template: Mapped["TaskTemplate"] = relationship()  # pyright: ignore[reportUndefinedVariable]  # noqa: F821
    task: Mapped["Task | None"] = relationship()  # pyright: ignore[reportUndefinedVariable]  # noqa: F821

    __table_args__: tuple[Index, ...] = (
        Index("ix_task_completions_user_id", "user_id"),
        Index("ix_task_completions_template_id", "template_id"),
        Index("ix_task_completions_completed_at", "completed_at"),
        Index("ix_task_completions_user_template_date", "user_id", "template_id", "completed_at"),
    )
