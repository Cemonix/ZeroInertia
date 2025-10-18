from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Project(Base):
    __tablename__: str = "projects"

    # Primary key with UUID
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    # Project fields - required
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    order_index: Mapped[int] = mapped_column(default=0, nullable=False)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    parent_id: Mapped[UUID | None] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="projects")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821
    parent: Mapped["Project | None"] = relationship(remote_side=[id], back_populates="subprojects")
    subprojects: Mapped[list["Project"]] = relationship(back_populates="parent")
    sections: Mapped[list["Section"]] = relationship(back_populates="project", cascade="all, delete-orphan")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821
    tasks: Mapped[list["Task"]] = relationship(back_populates="project", cascade="all, delete-orphan")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821

    # Constraints and Indexes
    __table_args__: tuple[Index] = (
        Index("ix_projects_user_id", "user_id"),
    )
