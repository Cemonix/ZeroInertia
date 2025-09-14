from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.task import PriorityLevel


class TaskTemplate(Base):
    __tablename__: str = "task_templates"

    # Primary key with UUID
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(String(1000), default=None)
    default_priority: Mapped[PriorityLevel] = mapped_column(default=PriorityLevel.LOW)

    # Recurrence settings
    recurrence_pattern: Mapped[str] = mapped_column(String(50))  # "daily", "weekly", "monthly"
    recurrence_interval: Mapped[int] = mapped_column(default=1)  # every N days/weeks/months

    # Relationships
    user: Mapped["User"] = relationship(back_populates="task_templates")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821
    tasks: Mapped[list["Task"]] = relationship(back_populates="template")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821

    __table_args__: tuple[Index, ...] = (
        Index("ix_task_templates_user_id", "user_id"),
        Index("ix_task_templates_recurrence_pattern", "recurrence_pattern"),
    )
