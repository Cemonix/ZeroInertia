from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy import Date, ForeignKey, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Streak(Base):
    __tablename__: str = "streaks"

    # Primary key with UUID
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    # Streak fields - required
    current_streak: Mapped[int] = mapped_column(default=0, nullable=False)
    longest_streak: Mapped[int] = mapped_column(default=0, nullable=False)
    last_activity_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="streaks")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821

    # Constraints and Indexes
    __table_args__: tuple[Index] = (
        Index("ix_streaks_user_id", "user_id"),
    )
