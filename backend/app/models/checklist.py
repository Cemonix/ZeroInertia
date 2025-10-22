from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base import Base


class CheckList(Base):
    __tablename__: str = "checklists"

    # Primary key with UUID
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    # CheckList fields
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    order_index: Mapped[int] = mapped_column(default=0, nullable=False)

    # Foreign keys
    task_id: Mapped[UUID] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    task: Mapped["Task"] = relationship(  # pyright: ignore[reportUndefinedVariable]  # noqa: F821
        back_populates="checklists"
    )
    items: Mapped[list["CheckListItem"]] = relationship(
        back_populates="checklist",
        cascade="all, delete-orphan",
        order_by="CheckListItem.order_index",
    )

    # Constraints and Indexes
    __table_args__: tuple[Index] = (Index("ix_checklists_task_id", "task_id"),)


class CheckListItem(Base):
    __tablename__: str = "checklist_items"

    # Primary key with UUID
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    # CheckListItem fields
    text: Mapped[str] = mapped_column(Text, nullable=False)
    completed: Mapped[bool] = mapped_column(default=False, nullable=False)
    order_index: Mapped[int] = mapped_column(default=0, nullable=False)

    # Foreign keys
    checklist_id: Mapped[UUID] = mapped_column(
        ForeignKey("checklists.id", ondelete="CASCADE"), nullable=False
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    checklist: Mapped["CheckList"] = relationship(back_populates="items")

    # Constraints and Indexes
    __table_args__: tuple[Index] = (
        Index("ix_checklist_items_checklist_id", "checklist_id"),
    )
