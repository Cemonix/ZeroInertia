from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class PushSubscription(Base):
    """
    Stores FCM (Firebase Cloud Messaging) push notification subscriptions for users.
    Each user can have multiple subscriptions (different browsers/devices).

    NOTE: The 'endpoint' field stores the FCM registration token.
    """
    __tablename__: str = "push_subscriptions"

    # Primary key with UUID
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    # Foreign key to user
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # FCM registration token (stored as 'endpoint' for compatibility)
    endpoint: Mapped[str] = mapped_column(Text, nullable=False, unique=True)

    # Optional metadata
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)  # Browser/device info

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="push_subscriptions")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821

    # Constraints and Indexes
    __table_args__: tuple[Index, Index] = (
        Index("ix_push_subscriptions_user_id", "user_id"),
        Index("ix_push_subscriptions_endpoint", "endpoint"),
    )
