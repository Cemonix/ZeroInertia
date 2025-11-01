from datetime import datetime
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy import DateTime, ForeignKey, Index, String, Table, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

task_labels = Table(
    "task_labels",
    Base.metadata,
    sa.Column(
        "task_id",
        sa.Uuid(as_uuid=True),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    sa.Column(
        "label_id",
        sa.Uuid(as_uuid=True),
        ForeignKey("labels.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    sa.Column(
        "created_at",
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    ),
    Index("ix_task_labels_task_id", "task_id"),
    Index("ix_task_labels_label_id", "label_id"),
)


class Label(Base):
    __tablename__: str = "labels"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    color: Mapped[str | None] = mapped_column(String(7), nullable=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    order_index: Mapped[int] = mapped_column(default=0, nullable=False)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user: Mapped["User"] = relationship(back_populates="labels")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821
    tasks: Mapped[list["Task"]] = relationship(  # pyright: ignore[reportUndefinedVariable]  # noqa: F821
        secondary=task_labels,
        back_populates="labels",
    )

    __table_args__: tuple[Index, UniqueConstraint] = (
        Index("ix_labels_user_id", "user_id"),
        UniqueConstraint("user_id", "name", name="uq_labels_user_id_name"),
    )
