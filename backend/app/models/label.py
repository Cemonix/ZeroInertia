from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Label(Base):
    __tablename__: str = "labels"

    # Primary key with UUID
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    name: Mapped[str] = mapped_column(String(100))
    color: Mapped[str] = mapped_column(String(7), default="#6B7280")  # hex color code

    # Relationships
    user: Mapped["User"] = relationship(back_populates="labels")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821
    tasks: Mapped[list["Task"]] = relationship(  # pyright: ignore[reportUndefinedVariable]  # noqa: F821
        back_populates="labels", secondary="task_labels"
    )

    __table_args__: tuple[Index | UniqueConstraint, ...] = (
        Index("ix_user_id", "user_id"),
        UniqueConstraint("user_id", "name", name="uq_user_label_name"),
    )
