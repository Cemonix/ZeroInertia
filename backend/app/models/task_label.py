from sqlalchemy import Column, ForeignKey, Index, Table

from app.models.base import Base

# Association table for many-to-many relationship between Task and Label
task_label_association = Table(
    "task_labels",
    Base.metadata,
    Column("task_id", ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True),  # pyright: ignore[reportUnknownArgumentType]
    Column("label_id", ForeignKey("labels.id", ondelete="CASCADE"), primary_key=True),  # pyright: ignore[reportUnknownArgumentType]
    Index("ix_task_labels_task_id", "task_id"),
    Index("ix_task_labels_label_id", "label_id"),
)
