from uuid import UUID, uuid4

from sqlalchemy import Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Text

from app.models.base import Base


class Priority(Base):
    __tablename__: str = "priorities"

    # Primary key with UUID
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    # Priority fields
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    color: Mapped[str] = mapped_column(String(7), nullable=False)  # Hex color code
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    order_index: Mapped[int] = mapped_column(default=0, nullable=False)

    # Relationships
    tasks: Mapped[list["Task"]] = relationship(  # pyright: ignore[reportUndefinedVariable]  # noqa: F821
        back_populates="priority"
    )

    # Constraints and Indexes
    # TODO: Redundant with unique=True on name, can be removed
    __table_args__: tuple[Index] = (
        Index("ix_priorities_name", "name"),
    )
