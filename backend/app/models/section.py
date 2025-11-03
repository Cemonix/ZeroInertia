from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Section(Base):
    __tablename__: str = "sections"

    # Primary key with UUID
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    # Section fields - required
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    order_index: Mapped[int] = mapped_column(default=0, nullable=False)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="sections")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821
    project: Mapped["Project"] = relationship(back_populates="sections")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821
    tasks: Mapped[list["Task"]] = relationship(back_populates="section", cascade="all, delete-orphan")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821
    recurring_tasks: Mapped[list["RecurringTask"]] = relationship(back_populates="section", cascade="all, delete-orphan")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821

    # Constraints and Indexes
    __table_args__: tuple[Index] = (
        Index("ix_sections_user_id", "user_id"),
    )
