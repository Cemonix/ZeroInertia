from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class TaskStreak(Base):
    __tablename__: str = "task_streaks"

    # Primary key with UUID
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    template_id: Mapped[UUID] = mapped_column(ForeignKey("task_templates.id", ondelete="CASCADE"), nullable=False)

    current_streak: Mapped[int] = mapped_column(default=0)
    longest_streak: Mapped[int] = mapped_column(default=0)
    last_completion_date: Mapped[datetime | None] = mapped_column(default=None)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="task_streaks")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821
    template: Mapped["TaskTemplate"] = relationship()  # pyright: ignore[reportUndefinedVariable]  # noqa: F821

    __table_args__: tuple[Index | UniqueConstraint, ...] = (
        Index("ix_user_id", "user_id"),
        Index("ix_template_id", "template_id"),
        UniqueConstraint("user_id", "template_id", name="uq_user_template_streak"),
    )
