from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Index, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class NoteLink(Base):
    __tablename__: str = "note_links"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    source_note_id: Mapped[UUID] = mapped_column(
        ForeignKey("notes.id", ondelete="CASCADE"),
        nullable=False,
    )
    target_note_id: Mapped[UUID] = mapped_column(
        ForeignKey("notes.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    source_note: Mapped["Note"] = relationship(  # pyright: ignore[reportUndefinedVariable]  # noqa: F821
        foreign_keys=[source_note_id],
        back_populates="outgoing_links",
    )
    target_note: Mapped["Note"] = relationship(  # pyright: ignore[reportUndefinedVariable]  # noqa: F821
        foreign_keys=[target_note_id],
        back_populates="incoming_links",
    )

    __table_args__: tuple[Index, Index, UniqueConstraint] = (
        Index("ix_note_links_source", "source_note_id"),
        Index("ix_note_links_target", "target_note_id"),
        UniqueConstraint("source_note_id", "target_note_id", name="uq_note_link"),
    )
